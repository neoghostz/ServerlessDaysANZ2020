class RequiredFieldError(Exception):
    pass


class UnknownQueryParameter(Exception):
    pass


class MissingReponseFields(Exception):
    pass


class InvalidateSchema(Exception):
    pass


class S3WriteFailure(Exception):
    pass


class S3ReadFailure(Exception):
    pass


class DynamoDBWriteFailure(Exception):
    pass


class DynamoDBReadFailure(Exception):
    pass
