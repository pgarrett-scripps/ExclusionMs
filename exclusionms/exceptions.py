class IncorrectToleranceException(Exception):
    pass


class UnexpectedStatusCodeException(Exception):

    def __init__(self, status_code: int, expected_status_code: int, detail: str):
        super().__init__(f'Expected Status Code: {expected_status_code}, but received: {status_code}. detail: {detail}')
