from aiogram.filters import BaseFilter
from aiogram.types import Message

from db.User import User


class UserAuthFilter(BaseFilter):
    def __init__(self,
                 admin: bool = None,
                 ):
        self.admin = admin

    async def __call__(self, message: Message, user: User) -> bool:
        if user is None:
            return False

        if self.admin:
            return user.admin

        return True
