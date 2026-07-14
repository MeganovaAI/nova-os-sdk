from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_auth import DeploymentAuth
    from ..models.deployment_models import DeploymentModels


T = TypeVar("T", bound="Deployment")


@_attrs_define
class Deployment:
    """Minimal, derive-friendly capabilities read so a client (web/iOS) can
    discover what this Nova OS instance supports without probing each
    endpoint. Per the contract-unification design (D1, lean: derive),
    this is intentionally small — the persona manifest
    (`GET /agents/v1/personas`) remains the source of truth for *which*
    agents exist; this read surfaces server-level feature flags, model
    tiers, enabled locales, and the auth contract clients need at boot.
    All fields are advisory; absence means "not advertised", not "off".

        Attributes:
            version (str): Nova OS server version (e.g. "v0.1.9"). "dev"/"unknown" on unstamped builds.
            capabilities (list[str]): Stable string labels for optional server features a client may
                branch on (e.g. "observational_memory", "report_generator",
                "async_jobs", "workflows", "knowledge_gate", "ag_ui_streaming").
                Open-ended — unknown labels are ignored by older clients.
            models (DeploymentModels | Unset): Resolved model tiers (advisory; no secrets). Lets a client show
                "powered by" / pick a tier without hardcoding model ids.
            locales (list[str] | Unset): Enabled UI locales; first is the default (e.g. ["en","zh-CN"]).
            auth (DeploymentAuth | Unset): The interactive-login contract clients should use. OIDC details
                live in the hand-authored `docs/oidc-client-flow.md`; this block
                only advertises the issuer + whether OIDC is enabled so a client
                can construct the Auth-Code+PKCE flow.
    """

    version: str
    capabilities: list[str]
    models: DeploymentModels | Unset = UNSET
    locales: list[str] | Unset = UNSET
    auth: DeploymentAuth | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        capabilities = self.capabilities

        models: dict[str, Any] | Unset = UNSET
        if not isinstance(self.models, Unset):
            models = self.models.to_dict()

        locales: list[str] | Unset = UNSET
        if not isinstance(self.locales, Unset):
            locales = self.locales

        auth: dict[str, Any] | Unset = UNSET
        if not isinstance(self.auth, Unset):
            auth = self.auth.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "capabilities": capabilities,
            }
        )
        if models is not UNSET:
            field_dict["models"] = models
        if locales is not UNSET:
            field_dict["locales"] = locales
        if auth is not UNSET:
            field_dict["auth"] = auth

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_auth import DeploymentAuth
        from ..models.deployment_models import DeploymentModels

        d = dict(src_dict)
        version = d.pop("version")

        capabilities = cast(list[str], d.pop("capabilities"))

        _models = d.pop("models", UNSET)
        models: DeploymentModels | Unset
        if isinstance(_models, Unset):
            models = UNSET
        else:
            models = DeploymentModels.from_dict(_models)

        locales = cast(list[str], d.pop("locales", UNSET))

        _auth = d.pop("auth", UNSET)
        auth: DeploymentAuth | Unset
        if isinstance(_auth, Unset):
            auth = UNSET
        else:
            auth = DeploymentAuth.from_dict(_auth)

        deployment = cls(
            version=version,
            capabilities=capabilities,
            models=models,
            locales=locales,
            auth=auth,
        )

        deployment.additional_properties = d
        return deployment

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
