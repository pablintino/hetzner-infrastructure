class ConfigurationException(Exception):
    pass


class UnexpectedTerraformFailureException(Exception):
    pass


class SSHKeysException(Exception):
    pass


class PackageManagerException(Exception):
    pass


class UnsupportedChangeException(Exception):
    pass