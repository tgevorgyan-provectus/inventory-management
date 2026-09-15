<template>
  <aside class="sidebar">
    <div class="logo">
      <h1>{{ t('nav.companyName') }}</h1>
      <span class="subtitle">{{ t('nav.subtitle') }}</span>
    </div>

    <nav class="nav-links">
      <router-link to="/" :class="{ active: $route.path === '/' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </svg>
        {{ t('nav.overview') }}
      </router-link>
      <router-link to="/inventory" :class="{ active: $route.path === '/inventory' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M21 8l-9-5-9 5 9 5 9-5z" />
          <path d="M3 8v8l9 5 9-5V8" />
          <path d="M12 13v8" />
        </svg>
        {{ t('nav.inventory') }}
      </router-link>
      <router-link to="/orders" :class="{ active: $route.path === '/orders' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="9" cy="21" r="1" />
          <circle cx="20" cy="21" r="1" />
          <path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6" />
        </svg>
        {{ t('nav.orders') }}
      </router-link>
      <router-link to="/spending" :class="{ active: $route.path === '/spending' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v10M9.5 9.5c0-1.1 1.12-2 2.5-2s2.5.9 2.5 2-1.12 2-2.5 2-2.5.9-2.5 2 1.12 2 2.5 2 2.5-.9 2.5-2" />
        </svg>
        {{ t('nav.finance') }}
      </router-link>
      <router-link to="/demand" :class="{ active: $route.path === '/demand' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M3 3v18h18" />
          <path d="M7 15l4-6 3 4 5-8" />
        </svg>
        {{ t('nav.demandForecast') }}
      </router-link>
      <router-link to="/reports" :class="{ active: $route.path === '/reports' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M14 3H6a2 2 0 00-2 2v14a2 2 0 002 2h12a2 2 0 002-2V9z" />
          <path d="M14 3v6h6" />
          <path d="M9 13h6M9 17h6" />
        </svg>
        Reports
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'
import ProfileMenu from './ProfileMenu.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'

export default {
  name: 'Sidebar',
  components: {
    ProfileMenu,
    LanguageSwitcher
  },
  emits: ['show-profile-details', 'show-tasks'],
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
}

.logo {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.logo h1 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.subtitle {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 400;
}

/* flex + min-height:0 lets this list scroll without clipping footer dropdowns */
.nav-links {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem 0.75rem;
}

.nav-links a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-links a svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-links a:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.nav-links a.active {
  color: #2563eb;
  background: #eff6ff;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem 0.75rem;
  border-top: 1px solid #e2e8f0;
}

/* dropdowns default to opening downward; flip upward so they don't render off-screen */
.sidebar-footer :deep(.dropdown-menu) {
  top: auto;
  bottom: calc(100% + 0.5rem);
  left: 0;
  right: auto;
  min-width: 0;
  width: 100%;
}
</style>
