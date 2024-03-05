from tortoise.models import Model
from tortoise import fields

from db.fields import PermissionField, AutoNowDatetimeField


class User(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    name = fields.CharField(max_length=129)
    admin = PermissionField()

    created_at = AutoNowDatetimeField()


class Ban(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    banned_by = fields.BigIntField(null=True)
    reason = fields.TextField()

    created_at = AutoNowDatetimeField()


class Notify(Model):
    text = fields.TextField()
    queue = fields.ManyToManyField('models.User')

    initiated_by = fields.ForeignKeyField('models.User', related_name='notifys_inited')
    init_queue_size = fields.BigIntField()
    errors = fields.BigIntField(default=0)

    created_at = AutoNowDatetimeField()

    @property
    def completed(self):
        return len(self.queue) == 0
