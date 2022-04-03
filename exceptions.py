class ResponseStatusCodeError(Exception):
    """Исключение вызывается в случае неправильного ответа от сервера."""
    pass

class HomeworkStatusNotExist(Exception):
    """Исключение вызывается в случае отсутствия верноо статуса."""
    pass
