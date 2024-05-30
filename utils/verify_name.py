def verify_name(name: str):
    for el in name:
        if not el.isnumeric() and not el.isalpha():
            return False

    return True
