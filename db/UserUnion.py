from random import randint

from tortoise.models import Model
from tortoise import fields


class Group(Model):
    name = fields.CharField(max_length=32)
    owner = fields.ForeignKeyField('models.User')

    members = fields.ManyToManyField('models.User')

    notify_perdish = fields.BooleanField(default=True)
    password = fields.IntField()

    @staticmethod
    def generate_password() -> int:
        return randint(100000, 999999)

