from datetime import datetime
from enum import IntEnum

from tortoise.models import Model
from tortoise import fields

from db.fields import AutoNowDatetimeField


class SretType(IntEnum):
    SRET = 1
    DRISHET = 2
    PERNUL = 3


class SretSession(Model):
    user = fields.ForeignKeyField('models.User')

    start = AutoNowDatetimeField()
    end = fields.DatetimeField(null=True, default=None)

    sret_type = fields.IntEnumField(SretType)
