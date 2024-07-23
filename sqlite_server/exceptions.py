class SqliteServerException(BaseException):
    # Generic error caused by sqlite_server
    pass


class DatabaseConnectionLost(SqliteServerException):
    pass


class MalformedSchema(SqliteServerException):
    pass


class InvalidAPIPath(SqliteServerException):
    pass


