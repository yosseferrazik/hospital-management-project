from app.routes.base import make_crud_blueprint
from app.services.operating_theater_service import create_operating_theater, get_operating_theaters, get_operating_theater, update_operating_theater, delete_operating_theater

operating_theater_bp = make_crud_blueprint(
    "operating_theater", "/api/operating_theaters",
    create_fn=create_operating_theater, list_fn=get_operating_theaters, get_fn=get_operating_theater,
    update_fn=update_operating_theater, delete_fn=delete_operating_theater,
    create_required=["theater_code", "floor_id"], update_required=["theater_code", "floor_id"],
    serialize=lambda t: {"theater_id": t.theater_id, "theater_code": t.theater_code, "floor_id": t.floor_id},
)
