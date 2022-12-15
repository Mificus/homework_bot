class SendMessageError(Exception):
    """Ошибка отправки сообщения"""
    pass

class GetApiAnswerError(Exception):
    """Ошибка запроса статуса домашней работы"""
    pass

class UnavailableEndpoint(Exception):
    """Ошибка Эндпойнта"""
    pass

class ResponseDateError(Exception):
    """Ошибка получаемых значенией"""
    pass