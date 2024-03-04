from datetime import datetime

from tortoise.models import Model
from tortoise import fields

from db.fields import PermissionField


class User(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    name = fields.CharField(max_length=129)
    admin = PermissionField()

    created_at = fields.DatetimeField(default=datetime.now)


class Ban(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    banned_by = fields.BigIntField(null=True)
    reason = fields.TextField()

    created_at = fields.DatetimeField(default=datetime.now)
