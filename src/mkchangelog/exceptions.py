class MKChangelogError(Exception):
    """Base class for mkchangelog erros."""


class MKChangelogRuntimeError(MKChangelogError):
    """Runtime errors."""


class MKChangelogTemplateError(MKChangelogRuntimeError):
    """Error during execution of template"""


class MKChangelogFilterError(MKChangelogTemplateError):
    """Error during execution of template filter"""
