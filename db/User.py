from tortoise.models import Model
from tortoise import fields

from db.fields import PermissionField


class User(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    name = fields.CharField(max_length=64, default='New user')
    admin = PermissionField()

