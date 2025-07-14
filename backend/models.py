from tortoise.models import Model
from tortoise import fields

class FileModel(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField(unique=True)
    content = fields.BinaryField()
    created_at = fields.DatetimeField(auto_now_add=True)

