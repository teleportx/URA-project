import hashlib
import secrets
import string
from typing import Tuple

from tortoise import fields
from tortoise.exceptions import ValidationError
from tortoise.models import Model
from tortoise.validators import MinLengthValidator, Validator

from db.fields import AutoNowDatetimeField

letters = string.ascii_letters + string.digits


class TokenNameValidator(Validator):
    def __call__(self, value: str):
        for i in range(len(value)):
            char = value[i]
            if not char.isnumeric() and not ('a' <= char <= 'z') and char != '_':
                raise ValidationError(f'Unexpected char "{char}" in token name "{value}" on position {i + 1}', i)


class ApiToken(Model):
    id = fields.UUIDField(pk=True)
    token = fields.CharField(unique=True, max_length=64, validators=[MinLengthValidator(64)])
    owner = fields.ForeignKeyField('models.User', related_name='tokens_owned')
    name = fields.CharField(max_length=64, validators=[MinLengthValidator(3), TokenNameValidator()])

    created_at = AutoNowDatetimeField()
    valid = fields.BooleanField(default=True)

    @classmethod
    def hash_token(cls, value: str):
        return hashlib.sha256(value.encode()).hexdigest()

    @classmethod
    def generate_token(cls) -> Tuple[str, str]:
        token = ''.join(secrets.choice(letters) for _ in range(64))

        return token, cls.hash_token(token)
