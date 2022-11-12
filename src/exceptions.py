from sanic import exceptions


class InvalidUsage(exceptions.SanicException):
    status_code = 400


class PaymentError(exceptions.SanicException):
    status_code = 402
    message = "Not enough money in the account"


class NotFoundInstance(exceptions.SanicException):
    status_code = 404
    message = "Not found instance"


class Forbidden(exceptions.SanicException):
    status_code = 403
    message = "You don't have access"
