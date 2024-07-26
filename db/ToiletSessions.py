from enum import IntEnum

from tortoise import fields
from tortoise.models import Model

from db.fields import AutoNowDatetimeField


class SretType(IntEnum):
    SRET = 1
    DRISHET = 2
    PERNUL = 3


class SretSession(Model):
    message_id = fields.BigIntField()
    user = fields.ForeignKeyField('models.User')

    start = AutoNowDatetimeField(index=True)
    end = fields.DatetimeField(null=True, default=None)

    autoend = fields.BooleanField()
    sret_type = fields.IntEnumField(SretType)
