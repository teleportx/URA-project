from tortoise import fields
from tortoise.models import Model

from db.fields import AutoNowDatetimeField
from utils.generate_random_secret import generate_random_secret


def generate_password() -> str:
    return generate_random_secret(8).lower()


class Group(Model):
    name = fields.CharField(max_length=32)
    owner = fields.ForeignKeyField('models.User', related_name='groups_owned')

    members = fields.ManyToManyField('models.User', related_name='groups_member', through='group_member')
    requests = fields.ManyToManyField('models.User', related_name='groups_requested', through='group_request')

    notify_perdish = fields.BooleanField(default=True)
    password = fields.CharField(default=generate_password, max_length=8)

    created_at = AutoNowDatetimeField()


class FriendRequest(Model):
    user = fields.ForeignKeyField('models.User', related_name='friends_requested')
    requested_user = fields.ForeignKeyField('models.User', related_name='friend_requests')
    message_id = fields.BigIntField(null=True)


class Channel(Model):
    channel_id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=128)

    members = fields.ManyToManyField('models.User', related_name='channels_member', through='channel_member')
    requests = fields.ManyToManyField('models.User', related_name='channels_requested', through='channel_request')

    notify_perdish = fields.BooleanField(default=True)
    password = fields.CharField(default=generate_password, max_length=8)

    created_at = AutoNowDatetimeField()
