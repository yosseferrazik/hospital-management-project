"""Floor CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.floor_service import create_floor, get_floors, get_floor, update_floor, delete_floor

floor_bp = make_crud_blueprint(
    "floor", "/api/floors",
    create_fn=create_floor, list_fn=get_floors, get_fn=get_floor, update_fn=update_floor, delete_fn=delete_floor,
    create_required=["floor_number"], update_required=["floor_number"],
    serialize=lambda f: {"floor_id": f.floor_id, "floor_number": f.floor_number},
)
