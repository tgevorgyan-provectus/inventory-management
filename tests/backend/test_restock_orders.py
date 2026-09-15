"""
Tests for restocking order API endpoints.
"""
from datetime import datetime

import pytest


@pytest.fixture
def restock_payload():
    """Valid restock order request body."""
    return {
        "budget": 25000,
        "items": [
            {
                "sku": "FLT-405",
                "name": "Hydraulic Filter Cartridge",
                "quantity": 570,
                "unit_cost": 22.40,
                "line_total": 12768.00
            },
            {
                "sku": "WDG-001",
                "name": "Industrial Widget Type A",
                "quantity": 270,
                "unit_cost": 42.50,
                "line_total": 11475.00
            }
        ]
    }


class TestRestockOrderEndpoints:
    """Test suite for restocking order endpoints."""

    def test_get_all_restock_orders(self, client):
        """Test getting all submitted restock orders."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_create_restock_order(self, client, restock_payload):
        """Test submitting a restock order."""
        response = client.post("/api/restock-orders", json=restock_payload)
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "order_number" in data
        assert data["status"] == "Submitted"
        assert data["budget"] == 25000
        assert len(data["items"]) == 2

    def test_create_restock_order_total_cost_calculation(self, client, restock_payload):
        """Test that total cost is the sum of the submitted line totals."""
        response = client.post("/api/restock-orders", json=restock_payload)
        data = response.json()

        expected_total = sum(item["line_total"] for item in restock_payload["items"])
        assert abs(data["total_cost"] - expected_total) < 0.01

    def test_create_restock_order_lead_time(self, client, restock_payload):
        """Test that expected delivery is the lead time after submission."""
        response = client.post("/api/restock-orders", json=restock_payload)
        data = response.json()

        assert data["lead_time_days"] == 14

        submitted = datetime.fromisoformat(data["submitted_date"])
        delivery = datetime.fromisoformat(data["expected_delivery"])
        assert (delivery - submitted).days == 14

    def test_create_restock_order_date_format(self, client, restock_payload):
        """Test that restock order dates include a time component."""
        response = client.post("/api/restock-orders", json=restock_payload)
        data = response.json()

        assert "T" in data["submitted_date"]
        assert "T" in data["expected_delivery"]

    def test_create_restock_order_preserves_items(self, client, restock_payload):
        """Test that submitted line items are returned unchanged."""
        response = client.post("/api/restock-orders", json=restock_payload)
        data = response.json()

        for submitted, returned in zip(restock_payload["items"], data["items"]):
            assert returned["sku"] == submitted["sku"]
            assert returned["quantity"] == submitted["quantity"]
            assert abs(returned["unit_cost"] - submitted["unit_cost"]) < 0.01

    def test_create_restock_order_invalid_body(self, client):
        """Test that a request missing required fields is rejected."""
        response = client.post("/api/restock-orders", json={"budget": 25000})
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_created_restock_order_is_listed(self, client, restock_payload):
        """Test that a submitted order appears in the list endpoint."""
        create_response = client.post("/api/restock-orders", json=restock_payload)
        order_number = create_response.json()["order_number"]

        response = client.get("/api/restock-orders")
        assert response.status_code == 200

        order_numbers = [order["order_number"] for order in response.json()]
        assert order_number in order_numbers

    def test_restock_order_numbers_unique(self, client, restock_payload):
        """Test that each submitted order gets a distinct order number."""
        client.post("/api/restock-orders", json=restock_payload)
        client.post("/api/restock-orders", json=restock_payload)

        order_numbers = [order["order_number"] for order in client.get("/api/restock-orders").json()]
        assert len(order_numbers) == len(set(order_numbers))


class TestRestockDataIntegrity:
    """Test suite for the forecast/inventory data the restocking view depends on."""

    def test_all_forecast_skus_exist_in_inventory(self, client):
        """Every forecast SKU needs an inventory record to supply its unit cost."""
        forecasts = client.get("/api/demand").json()
        inventory_skus = {item["sku"] for item in client.get("/api/inventory").json()}

        for forecast in forecasts:
            assert forecast["item_sku"] in inventory_skus

    def test_forecast_items_have_positive_unit_cost(self, client):
        """Test that every forecast item can be priced."""
        forecasts = client.get("/api/demand").json()
        inventory = {item["sku"]: item for item in client.get("/api/inventory").json()}

        for forecast in forecasts:
            assert inventory[forecast["item_sku"]]["unit_cost"] > 0
