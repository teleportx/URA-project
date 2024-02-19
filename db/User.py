from datetime import datetime

from peewee import *

from .base import BaseModel


class PermissionField(BooleanField):
    PERMISSION_FIELD = True

    def __init__(self):
        super().__init__(default=False)


class User(BaseModel):
    uid = BigIntegerField(primary_key=True, unique=True)
    name = CharField(max_length=64)
    admin = PermissionField()
    sret = DateTimeField(null=True, default=None)


class SretSession(BaseModel):
    user = ForeignKeyField(User, on_delete='CASCADE')
    start = DateTimeField()
    end = DateTimeField(default=datetime.now)

    @classmethod
    def create_session(cls, user: User):
        cls.create(user=user, start=user.sret)
