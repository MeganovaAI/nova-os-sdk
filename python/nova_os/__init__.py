"""Nova OS SDK — partner integration for Nova OS.

See https://github.com/MeganovaAI/nova-os-sdk for documentation.
"""

from nova_os._version import __version__, OPENAPI_VERSION
from nova_os.client import Client
from nova_os.anthropic_compat import AnthropicCompatClient
from nova_os.errors import (
    NovaOSError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitedError,
    BillingError,
    UpstreamError,
    VertexSchemaError,
    ModelNotFoundError,
    InternalError,
)
from nova_os.callbacks import WebhookRouter
from nova_os.streaming import MessageStream

__all__ = [
    "__version__",
    "OPENAPI_VERSION",
    "Client",
    "AnthropicCompatClient",
    "NovaOSError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "RateLimitedError",
    "BillingError",
    "UpstreamError",
    "VertexSchemaError",
    "ModelNotFoundError",
    "InternalError",
    "WebhookRouter",
    "MessageStream",
]
