from app.models import db, DispensationItem


def create_dispensation_item(data):
    item = DispensationItem(
        dispensation_id=data["dispensation_id"],
        medication_id=data["medication_id"],
        quantity=data["quantity"],
        unit_price=data["unit_price"],
    )
    db.session.add(item)
    db.session.commit()
    return item


def get_dispensation_items():
    return DispensationItem.query.all()


def get_dispensation_item(item_id):
    return DispensationItem.query.get(item_id)


def update_dispensation_item(item_id, data):
    item = DispensationItem.query.get(item_id)
    if item:
        item.dispensation_id = data["dispensation_id"]
        item.medication_id = data["medication_id"]
        item.quantity = data["quantity"]
        item.unit_price = data["unit_price"]
        db.session.commit()
    return item


def delete_dispensation_item(item_id):
    item = DispensationItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return item