from tortoise import fields


class PermissionField(fields.BooleanField):
    PERMISSION_FIELD = True

    def __init__(self):
        super().__init__(default=False)
