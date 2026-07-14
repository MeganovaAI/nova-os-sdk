from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mcp_request_jsonrpc import McpRequestJsonrpc
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mcp_request_params import McpRequestParams


T = TypeVar("T", bound="McpRequest")


@_attrs_define
class McpRequest:
    """JSON-RPC 2.0 request envelope.

    Attributes:
        jsonrpc (McpRequestJsonrpc):
        method (str): One of initialize, tools/list, tools/call, resources/list, resources/read.
        id (Any | Unset): JSON-RPC request id (string, number, or null), echoed on the response.
        params (McpRequestParams | Unset): Method-specific parameters.
    """

    jsonrpc: McpRequestJsonrpc
    method: str
    id: Any | Unset = UNSET
    params: McpRequestParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        jsonrpc = self.jsonrpc.value

        method = self.method

        id = self.id

        params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jsonrpc": jsonrpc,
                "method": method,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mcp_request_params import McpRequestParams

        d = dict(src_dict)
        jsonrpc = McpRequestJsonrpc(d.pop("jsonrpc"))

        method = d.pop("method")

        id = d.pop("id", UNSET)

        _params = d.pop("params", UNSET)
        params: McpRequestParams | Unset
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = McpRequestParams.from_dict(_params)

        mcp_request = cls(
            jsonrpc=jsonrpc,
            method=method,
            id=id,
            params=params,
        )

        mcp_request.additional_properties = d
        return mcp_request

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
