from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mcp_response_jsonrpc import McpResponseJsonrpc
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mcp_response_error import McpResponseError
    from ..models.mcp_response_result import McpResponseResult


T = TypeVar("T", bound="McpResponse")


@_attrs_define
class McpResponse:
    """JSON-RPC 2.0 response envelope. Exactly one of result or error is present.

    Attributes:
        jsonrpc (McpResponseJsonrpc):
        id (Any): JSON-RPC request id (string, number, or null), echoed on the response.
        result (McpResponseResult | Unset):
        error (McpResponseError | Unset):
    """

    jsonrpc: McpResponseJsonrpc
    id: Any
    result: McpResponseResult | Unset = UNSET
    error: McpResponseError | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        jsonrpc = self.jsonrpc.value

        id = self.id

        result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jsonrpc": jsonrpc,
                "id": id,
            }
        )
        if result is not UNSET:
            field_dict["result"] = result
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mcp_response_error import McpResponseError
        from ..models.mcp_response_result import McpResponseResult

        d = dict(src_dict)
        jsonrpc = McpResponseJsonrpc(d.pop("jsonrpc"))

        id = d.pop("id")

        _result = d.pop("result", UNSET)
        result: McpResponseResult | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = McpResponseResult.from_dict(_result)

        _error = d.pop("error", UNSET)
        error: McpResponseError | Unset
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = McpResponseError.from_dict(_error)

        mcp_response = cls(
            jsonrpc=jsonrpc,
            id=id,
            result=result,
            error=error,
        )

        mcp_response.additional_properties = d
        return mcp_response

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
