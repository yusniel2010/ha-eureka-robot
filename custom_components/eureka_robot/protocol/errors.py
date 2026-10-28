"""Protocol exceptions."""


class EurekaError(Exception):
    """Base protocol error."""


class EurekaConnectionError(EurekaError):
    """No matching response received."""


class EurekaProtocolError(EurekaError, ValueError):
    """Malformed or unsupported response."""


class EurekaCommandError(EurekaError, ValueError):
    """Robot rejected a command."""


class EurekaOutcomeUnknownError(EurekaConnectionError):
    """Command may have been delivered, but no acknowledgement was received."""
