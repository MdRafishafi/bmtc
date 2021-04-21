import uuid
from app import db


def generate_id(table_data: db.Model):
    uid = str(uuid.uuid4()).replace('-', '')
    result = table_data.query.filter_by(id=uid).first()
    if not result:
        return uid
    else:
        generate_id(table_data)
