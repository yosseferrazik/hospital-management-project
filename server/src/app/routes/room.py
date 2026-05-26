"""Room CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.room_service import create_room, get_rooms, get_room, update_room, delete_room

room_bp = make_crud_blueprint(
    "room", "/api/rooms",
    create_fn=create_room, list_fn=get_rooms, get_fn=get_room, update_fn=update_room, delete_fn=delete_room,
    create_required=["room_number", "floor_id"], update_required=["room_number", "floor_id"],
    serialize=lambda r: {"room_id": r.room_id, "room_number": r.room_number, "floor_id": r.floor_id},
)
