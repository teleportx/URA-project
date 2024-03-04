from datetime import datetime
from enum import IntEnum

from tortoise.models import Model
from tortoise import fields


class SretType(IntEnum):
    SRET = 1
    DRISHET = 2
    PERNUL = 3


class SretSession(Model):
    user = fields.ForeignKeyField('models.User')

    start = fields.DatetimeField(default=datetime.now)
    end = fields.DatetimeField(null=True, default=None)

    sret_type = fields.IntEnumField(SretType)
