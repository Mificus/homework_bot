class TokensError(Exception):
    """Нет переменных окружения"""
    pass

class EndPointsError(Exception):
    """Ошибки 400, 401, 404"""
    pass

class SendMessageError(Exception):
    """Ошибка отправки сообщения"""
    pass

class GetApiAnswerError(Exception):
    """Ошибка запроса статуса домашней работы"""
    pass

class HomeworksKeyError(Exception):
    """Ошибка ключа homeworks"""
    pass

class UnavailableEndpoint(Exception):
    """Ошибка Эндпойнта"""
    pass