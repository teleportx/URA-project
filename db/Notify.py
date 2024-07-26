from tortoise import fields
from tortoise.models import Model

from db.fields import AutoNowDatetimeField


class Notify(Model):
    message_id = fields.BigIntField(pk=True, unique=True)

    initiated_by = fields.ForeignKeyField('models.User', related_name='notifys_inited')
    created_at = AutoNowDatetimeField()

    scheduled_users_count = fields.IntField()
    executed_users_count = fields.IntField(default=0)
