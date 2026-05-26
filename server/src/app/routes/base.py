"""Generic CRUD blueprint factory for standard REST endpoints."""

from flask import Blueprint, request, jsonify


def make_crud_blueprint(name, url_prefix, create_fn, list_fn, get_fn, update_fn, delete_fn,
                        create_required, update_required, serialize, id_route="/<int:record_id>"):
    """Create a Blueprint with standard CRUD routes for a given resource.

    Args:
        name: Blueprint registration name.
        url_prefix: URL prefix for all routes.
        create_fn, list_fn, get_fn, update_fn, delete_fn: Service-layer callables.
        create_required: Fields required for POST.
        update_required: Fields required for PUT.
        serialize: Callable to convert a model instance to a dict.
        id_route: URL pattern for single-resource routes.

    Returns:
        A configured Flask Blueprint.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)

    # --- POST: create a new record ---
    @bp.route("", methods=["POST"])
    def create():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        missing = [f for f in create_required if f not in data]
        if missing:
            return jsonify({"error": f"{', '.join(missing)} required"}), 400
        try:
            record = create_fn(data)
            return jsonify(serialize(record)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # --- GET: list all records ---
    @bp.route("", methods=["GET"])
    def list_records():
        return jsonify([serialize(r) for r in list_fn()])

    # --- GET: fetch a single record by ID ---
    @bp.route(id_route, methods=["GET"])
    def get(record_id):
        record = get_fn(record_id)
        if not record:
            return jsonify({"error": "Not found"}), 404
        return jsonify(serialize(record))

    # --- PUT: update an existing record ---
    @bp.route(id_route, methods=["PUT"])
    def update(record_id):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        missing = [f for f in update_required if f not in data]
        if missing:
            return jsonify({"error": f"{', '.join(missing)} required"}), 400
        try:
            record = update_fn(record_id, data)
            if not record:
                return jsonify({"error": "Not found"}), 404
            return jsonify({"message": "Updated"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # --- DELETE: remove a record ---
    @bp.route(id_route, methods=["DELETE"])
    def delete(record_id):
        try:
            record = delete_fn(record_id)
            if not record:
                return jsonify({"error": "Not found"}), 404
            return jsonify({"message": "Deleted"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return bp
