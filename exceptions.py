class ResponseStatusCodeError(Exception):
    """Исключение вызывается в случае неправильного ответа от сервера."""
    pass


class HomeworkStatusNotExist(Exception):
    """Исключение вызывается в случае отсутствия верного статуса."""
    pass


class WrongAPIKeys(Exception):
    """Исключение вызывается в случае отсутствия верных ключей."""
    pass
