"""Dispensation item CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.dispensation_item_service import create_dispensation_item, get_dispensation_items, get_dispensation_item, update_dispensation_item, delete_dispensation_item

dispensation_item_bp = make_crud_blueprint(
    "dispensation_item", "/api/dispensation_items",
    create_fn=create_dispensation_item, list_fn=get_dispensation_items, get_fn=get_dispensation_item,
    update_fn=update_dispensation_item, delete_fn=delete_dispensation_item,
    create_required=["dispensation_id", "medication_id", "quantity", "unit_price"],
    update_required=["dispensation_id", "medication_id", "quantity", "unit_price"],
    serialize=lambda i: {"item_id": i.item_id, "dispensation_id": i.dispensation_id, "medication_id": i.medication_id, "quantity": i.quantity, "unit_price": float(i.unit_price)},
)
