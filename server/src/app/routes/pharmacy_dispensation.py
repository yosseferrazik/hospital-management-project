from app.routes.base import make_crud_blueprint
from app.services.pharmacy_dispensation_service import create_pharmacy_dispensation, get_pharmacy_dispensations, get_pharmacy_dispensation, update_pharmacy_dispensation, delete_pharmacy_dispensation

pharmacy_dispensation_bp = make_crud_blueprint(
    "pharmacy_dispensation", "/api/pharmacy_dispensations",
    create_fn=create_pharmacy_dispensation, list_fn=get_pharmacy_dispensations, get_fn=get_pharmacy_dispensation,
    update_fn=update_pharmacy_dispensation, delete_fn=delete_pharmacy_dispensation,
    create_required=["admission_id"], update_required=["admission_id"],
    serialize=lambda d: {
        "dispensation_id": d.dispensation_id, "admission_id": d.admission_id,
        "dispensed_at": str(d.dispensed_at) if d.dispensed_at else None,
        "total_cost": float(d.total_cost), "notes": d.notes,
    },
)
