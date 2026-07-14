"""LibraOS SDK — partner integration for LibraOS.

See https://github.com/libraos/sdk for documentation.
"""

from libraos._version import __version__, OPENAPI_VERSION
from libraos.client import Client
from libraos.anthropic_compat import AnthropicCompatClient
from libraos.errors import (
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
    PersonaNotFound,
)
from libraos.callbacks import WebhookRouter
from libraos.streaming import MessageStream
from libraos.simulator import (
    Archetype,
    ArchetypeValidationError,
    SimulationResult,
    Turn,
    simulate,
)

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
    "PersonaNotFound",
    "WebhookRouter",
    "MessageStream",
    "Archetype",
    "ArchetypeValidationError",
    "SimulationResult",
    "Turn",
    "simulate",
]
