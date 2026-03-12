import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CartServiceClient:
    @classmethod
    def get_cart(cls, customer_id: int) -> dict:
        try:
            resp = requests.get(
                f"{settings.CART_SERVICE_URL}/internal/carts/{customer_id}/",
                timeout=5,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("CartService error for customer %s: %s", customer_id, exc)
            raise

    @classmethod
    def clear_cart(cls, customer_id: int) -> None:
        try:
            requests.delete(
                f"{settings.CART_SERVICE_URL}/api/cart/{customer_id}/clear/",
                timeout=5,
            )
        except requests.RequestException as exc:
            logger.warning("Failed to clear cart for customer %s: %s", customer_id, exc)


class PayServiceClient:
    @classmethod
    def process_payment(cls, order_id: int, customer_id: int, amount, method: str) -> dict:
        resp = requests.post(
            f"{settings.PAY_SERVICE_URL}/internal/payments/process/",
            json={
                "order_id": order_id,
                "customer_id": customer_id,
                "amount": str(amount),
                "method": method,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


class ShipServiceClient:
    @classmethod
    def create_shipment(cls, order_id: int, customer_id: int, shipping_address: str) -> dict:
        resp = requests.post(
            f"{settings.SHIP_SERVICE_URL}/internal/shipments/create/",
            json={
                "order_id": order_id,
                "customer_id": customer_id,
                "shipping_address": shipping_address,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
