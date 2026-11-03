class DomainError(Exception):
    def __init__(self, message: str, code: str = "INVALID_INPUT", status: int = 422):
        self.message, self.code, self.status = message, code, status
        super().__init__(message)
