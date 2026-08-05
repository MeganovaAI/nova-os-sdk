from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.native_job_status import NativeJobStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="NativeJob")


@_attrs_define
class NativeJob:
    """Async job state.

    Attributes:
        job_id (str | Unset):
        agent_id (str | Unset):
        status (NativeJobStatus | Unset): Job lifecycle status.
        created_at (datetime.datetime | Unset):
        started_at (datetime.datetime | Unset): Present once the job begins running.
        finished_at (datetime.datetime | Unset): Present once the job reaches a terminal state.
        event_count (int | Unset): Number of events emitted so far.
        result (str | Unset): Final output text (present when done).
        error (str | Unset): Failure message (present when failed).
        tokens_used (int | Unset):
    """

    job_id: str | Unset = UNSET
    agent_id: str | Unset = UNSET
    status: NativeJobStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    started_at: datetime.datetime | Unset = UNSET
    finished_at: datetime.datetime | Unset = UNSET
    event_count: int | Unset = UNSET
    result: str | Unset = UNSET
    error: str | Unset = UNSET
    tokens_used: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        agent_id = self.agent_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        started_at: str | Unset = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()

        finished_at: str | Unset = UNSET
        if not isinstance(self.finished_at, Unset):
            finished_at = self.finished_at.isoformat()

        event_count = self.event_count

        result = self.result

        error = self.error

        tokens_used = self.tokens_used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if finished_at is not UNSET:
            field_dict["finished_at"] = finished_at
        if event_count is not UNSET:
            field_dict["event_count"] = event_count
        if result is not UNSET:
            field_dict["result"] = result
        if error is not UNSET:
            field_dict["error"] = error
        if tokens_used is not UNSET:
            field_dict["tokens_used"] = tokens_used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        agent_id = d.pop("agent_id", UNSET)

        _status = d.pop("status", UNSET)
        status: NativeJobStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = NativeJobStatus(_status)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _started_at = d.pop("started_at", UNSET)
        started_at: datetime.datetime | Unset
        if isinstance(_started_at, Unset):
            started_at = UNSET
        else:
            started_at = isoparse(_started_at)

        _finished_at = d.pop("finished_at", UNSET)
        finished_at: datetime.datetime | Unset
        if isinstance(_finished_at, Unset):
            finished_at = UNSET
        else:
            finished_at = isoparse(_finished_at)

        event_count = d.pop("event_count", UNSET)

        result = d.pop("result", UNSET)

        error = d.pop("error", UNSET)

        tokens_used = d.pop("tokens_used", UNSET)

        native_job = cls(
            job_id=job_id,
            agent_id=agent_id,
            status=status,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            event_count=event_count,
            result=result,
            error=error,
            tokens_used=tokens_used,
        )

        native_job.additional_properties = d
        return native_job

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
