class Error(Exception):
    pass


class FilterError(Error):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class DoesNotExist(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass
