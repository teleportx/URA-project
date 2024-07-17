from tortoise import fields
from tortoise.models import Model

from db.fields import PermissionField, AutoNowDatetimeField


class User(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    name = fields.CharField(max_length=129)
    admin = PermissionField()

    friends = fields.ManyToManyField('models.User', related_name='friend_with', through='friend_user')
    mute_friend_requests = fields.BooleanField(default=False)

    autoend = fields.BooleanField(default=True)
    autoend_time = fields.SmallIntField(default=10)

    created_at = AutoNowDatetimeField()


class Ban(Model):
    uid = fields.BigIntField(pk=True, unique=True)
    banned_by = fields.BigIntField(null=True)
    reason = fields.TextField()

    created_at = AutoNowDatetimeField()


class Notify(Model):
    message_id = fields.BigIntField(pk=True, unique=True)

    initiated_by = fields.ForeignKeyField('models.User', related_name='notifys_inited')
    created_at = AutoNowDatetimeField()

    scheduled_users_count = fields.IntField()
    executed_users_count = fields.IntField(default=0)
