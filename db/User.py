from peewee import *

from .base import BaseModel


class PermissionField(BooleanField):
    PERMISSION_FIELD = True

    def __init__(self):
        super().__init__(default=False)


class User(BaseModel):
    uid = BigIntegerField(primary_key=True, unique=True)
    admin = PermissionField()
