from flask import Blueprint, request, jsonify
from app.services.dispensation_item_service import create_dispensation_item, get_dispensation_items, get_dispensation_item, update_dispensation_item, delete_dispensation_item

dispensation_item_bp = Blueprint("dispensation_item", __name__, url_prefix="/api/dispensation_items")


@dispensation_item_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "dispensation_id" not in data or "medication_id" not in data or "quantity" not in data or "unit_price" not in data:
        return jsonify({"error": "dispensation_id, medication_id, quantity, unit_price required"}), 400
    item = create_dispensation_item(data)
    return jsonify({"item_id": item.item_id}), 201


@dispensation_item_bp.route("", methods=["GET"])
def list_dispensation_items():
    items = get_dispensation_items()
    return jsonify([{
        "item_id": i.item_id,
        "dispensation_id": i.dispensation_id,
        "medication_id": i.medication_id,
        "quantity": i.quantity,
        "unit_price": float(i.unit_price)
    } for i in items])


@dispensation_item_bp.route("/<int:item_id>", methods=["GET"])
def get(item_id):
    item = get_dispensation_item(item_id)
    if not item:
        return jsonify({"error": "Dispensation item not found"}), 404
    return jsonify({
        "item_id": item.item_id,
        "dispensation_id": item.dispensation_id,
        "medication_id": item.medication_id,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price)
    })


@dispensation_item_bp.route("/<int:item_id>", methods=["PUT"])
def update(item_id):
    data = request.get_json()
    if not data or "dispensation_id" not in data or "medication_id" not in data or "quantity" not in data or "unit_price" not in data:
        return jsonify({"error": "dispensation_id, medication_id, quantity, unit_price required"}), 400
    item = update_dispensation_item(item_id, data)
    if not item:
        return jsonify({"error": "Dispensation item not found"}), 404
    return jsonify({"message": "Dispensation item updated"})


@dispensation_item_bp.route("/<int:item_id>", methods=["DELETE"])
def delete(item_id):
    item = delete_dispensation_item(item_id)
    if not item:
        return jsonify({"error": "Dispensation item not found"}), 404
    return jsonify({"message": "Dispensation item deleted"})