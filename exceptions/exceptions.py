import os


class ErrorCodeBaseException(Exception):
    def __init__(self, msg=None, err_code=None):
        super().__init__(msg)
        self.err_code = os.EX_CONFIG if not err_code else err_code


class ConfigurationException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_CONFIG if not code else code)


class UnexpectedTerraformFailureException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_IOERR if not code else code)


class SSHKeysException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_USAGE if not code else code)


class PackageManagerException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_IOERR if not code else code)


class UnsupportedChangeException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_IOERR if not code else code)


class CommandConfirmationException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_USAGE if not code else code)


class KubesprayCLusterCreationException(ErrorCodeBaseException):
    def __init__(self, msg=None, code=None):
        super().__init__(msg, os.EX_IOERR if not code else code)
