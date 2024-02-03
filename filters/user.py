from aiogram.filters import BaseFilter
from aiogram.types import Message

from db.User import User


class UserAuthFilter(BaseFilter):
    def __init__(self,
                 auth: bool = True,
                 admin: bool = None,
                 ):
        self.auth = auth
        self.admin = admin

    async def __call__(self, message: Message, user: User) -> bool:
        if self.auth is None:
            return True

        elif not self.auth:
            return user is None

        if user is None:
            return False

        if self.admin:
            return user.admin

        return True
