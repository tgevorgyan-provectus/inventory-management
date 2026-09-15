<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card">
        <label for="budget-slider" class="budget-label">
          {{ t('restocking.availableBudget') }}: <strong>{{ currencySymbol }}{{ budget.toLocaleString() }}</strong>
        </label>
        <input
          id="budget-slider"
          type="range"
          min="0"
          max="150000"
          step="1000"
          v-model.number="budget"
          class="budget-slider"
        />
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.budgetAllocated') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ totalCost.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
        </div>
        <div :class="['stat-card', remainingBudget < budget * 0.1 ? 'warning' : 'success']">
          <div class="stat-label">{{ t('restocking.budgetRemaining') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ remainingBudget.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.itemsRecommended') }}</div>
          <div class="stat-value">{{ recommendations.length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.totalUnits') }}</div>
          <div class="stat-value">{{ totalUnits.toLocaleString() }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }}</h3>
          <button
            class="place-order-btn"
            :disabled="recommendations.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="submitResult" class="order-placed-banner">
          {{ t('restocking.orderPlaced', { orderNumber: submitResult.order_number, date: formatDate(submitResult.expected_delivery) }) }}
        </div>

        <div v-if="submitError" class="error">{{ submitError }}</div>

        <p v-if="recommendations.length === 0" class="empty-state">
          {{ t('restocking.noRecommendations') }}
        </p>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.onHand') }}</th>
                <th>{{ t('restocking.table.forecast') }}</th>
                <th>{{ t('restocking.table.shortfall') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in recommendations" :key="rec.sku">
                <td><strong>{{ rec.sku }}</strong></td>
                <td>{{ translateProductName(rec.name) }}</td>
                <td class="numeric">{{ rec.on_hand.toLocaleString() }}</td>
                <td class="numeric">{{ rec.forecast.toLocaleString() }}</td>
                <td class="numeric">{{ rec.gap.toLocaleString() }}</td>
                <td class="numeric">{{ rec.quantity.toLocaleString() }}</td>
                <td class="numeric">{{ currencySymbol }}{{ rec.unit_cost.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                <td class="numeric"><strong>{{ currencySymbol }}{{ rec.line_total.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, currentLocale, translateProductName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const inventoryItems = ref([])
    const budget = ref(25000)
    const submitting = ref(false)
    const submitResult = ref(null)
    // Kept separate from `error` so a failed submit doesn't hide the whole planning view
    const submitError = ref(null)

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        const [forecastsData, inventoryData] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory()
        ])
        forecasts.value = forecastsData
        inventoryItems.value = inventoryData
      } catch (err) {
        error.value = 'Failed to load restocking data: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Greedy allocation: largest shortfall first, until budget runs out
    const recommendations = computed(() => {
      const bySku = new Map(inventoryItems.value.map(item => [item.sku, item]))

      const candidates = []
      for (const f of forecasts.value) {
        const item = bySku.get(f.item_sku)
        if (!item) continue
        const gap = f.forecasted_demand - item.quantity_on_hand
        if (gap <= 0) continue
        candidates.push({ item, forecast: f, gap })
      }

      candidates.sort((a, b) => b.gap - a.gap)

      const result = []
      let remaining = budget.value
      for (const { item, forecast, gap } of candidates) {
        const qty = Math.min(gap, Math.floor(remaining / item.unit_cost))
        if (qty > 0) {
          const line_total = qty * item.unit_cost
          result.push({
            sku: item.sku,
            name: item.name,
            on_hand: item.quantity_on_hand,
            forecast: forecast.forecasted_demand,
            gap,
            quantity: qty,
            unit_cost: item.unit_cost,
            line_total
          })
          remaining -= line_total
        }
      }
      return result
    })

    const totalCost = computed(() => recommendations.value.reduce((sum, r) => sum + r.line_total, 0))
    const remainingBudget = computed(() => budget.value - totalCost.value)
    const totalUnits = computed(() => recommendations.value.reduce((sum, r) => sum + r.quantity, 0))

    const formatDate = (dateString) => {
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const placeOrder = async () => {
      try {
        submitting.value = true
        submitError.value = null
        const items = recommendations.value.map(({ sku, name, quantity, unit_cost, line_total }) => ({
          sku, name, quantity, unit_cost, line_total
        }))
        submitResult.value = await api.createRestockOrder({ budget: budget.value, items })
      } catch (err) {
        submitError.value = 'Failed to place order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadData)

    return {
      t,
      loading,
      error,
      budget,
      submitting,
      submitResult,
      submitError,
      recommendations,
      totalCost,
      remainingBudget,
      totalUnits,
      currencySymbol,
      translateProductName,
      formatDate,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-label {
  display: block;
  font-size: 0.938rem;
  color: #334155;
  margin-bottom: 0.875rem;
}

.budget-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  appearance: none;
  background: #e2e8f0;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.budget-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.place-order-btn {
  padding: 0.5rem 1.25rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.order-placed-banner {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.empty-state {
  color: #64748b;
  font-size: 0.938rem;
  padding: 1.5rem 0;
}

.numeric {
  font-variant-numeric: tabular-nums;
}
</style>
