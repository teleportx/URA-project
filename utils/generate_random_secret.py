import secrets
import string

letters = string.ascii_letters + string.digits


def generate_random_secret(length: int) -> str:
    return ''.join(secrets.choice(letters) for _ in range(length))
