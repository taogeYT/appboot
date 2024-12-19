class Error(Exception):
    code = 500


class NotFound(Error):
    code = 404


class BadRequest(Error):
    code = 400


class Unauthorized(Error):
    code = 401


class Forbidden(Error):
    code = 403


class Conflict(Error):
    code = 409


class Unavailable(Error):
    code = 422


class FilterError(Error):
    code = 500


class InterfaceError(Error):
    code = 500


class DatabaseError(Error):
    code = 400


class DoesNotExist(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass
