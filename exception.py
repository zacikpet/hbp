class UserAlreadyExistsException(Exception):
    pass


class NoSuchArticleException(Exception):
    pass


class NoSuchUserException(Exception):
    pass


class InvalidPasswordException(Exception):
    pass


class UserNotVerifiedException(Exception):
    pass


class UserAlreadyVerifiedException(Exception):
    pass


class MissingFieldsException(Exception):
    def __init__(self, missing_fields):
        self.message = ', '.join(missing_fields)
        super().__init__(self.message)
