from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.job_status import JobStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error import Error
    from ..models.message_response import MessageResponse


T = TypeVar("T", bound="Job")


@_attrs_define
class Job:
    """
    Attributes:
        job_id (str):
        agent_id (str):
        status (JobStatus):
        created_at (datetime.datetime):
        employee_id (str | Unset):
        started_at (datetime.datetime | Unset):
        finished_at (datetime.datetime | Unset):
        result (MessageResponse | Unset):
        error (Error | Unset):
        event_count (int | Unset):
        instance_id (str | Unset):
    """

    job_id: str
    agent_id: str
    status: JobStatus
    created_at: datetime.datetime
    employee_id: str | Unset = UNSET
    started_at: datetime.datetime | Unset = UNSET
    finished_at: datetime.datetime | Unset = UNSET
    result: MessageResponse | Unset = UNSET
    error: Error | Unset = UNSET
    event_count: int | Unset = UNSET
    instance_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        agent_id = self.agent_id

        status = self.status.value

        created_at = self.created_at.isoformat()

        employee_id = self.employee_id

        started_at: str | Unset = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()

        finished_at: str | Unset = UNSET
        if not isinstance(self.finished_at, Unset):
            finished_at = self.finished_at.isoformat()

        result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        event_count = self.event_count

        instance_id = self.instance_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "agent_id": agent_id,
                "status": status,
                "created_at": created_at,
            }
        )
        if employee_id is not UNSET:
            field_dict["employee_id"] = employee_id
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if finished_at is not UNSET:
            field_dict["finished_at"] = finished_at
        if result is not UNSET:
            field_dict["result"] = result
        if error is not UNSET:
            field_dict["error"] = error
        if event_count is not UNSET:
            field_dict["event_count"] = event_count
        if instance_id is not UNSET:
            field_dict["instance_id"] = instance_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error import Error
        from ..models.message_response import MessageResponse

        d = dict(src_dict)
        job_id = d.pop("job_id")

        agent_id = d.pop("agent_id")

        status = JobStatus(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        employee_id = d.pop("employee_id", UNSET)

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

        _result = d.pop("result", UNSET)
        result: MessageResponse | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = MessageResponse.from_dict(_result)

        _error = d.pop("error", UNSET)
        error: Error | Unset
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = Error.from_dict(_error)

        event_count = d.pop("event_count", UNSET)

        instance_id = d.pop("instance_id", UNSET)

        job = cls(
            job_id=job_id,
            agent_id=agent_id,
            status=status,
            created_at=created_at,
            employee_id=employee_id,
            started_at=started_at,
            finished_at=finished_at,
            result=result,
            error=error,
            event_count=event_count,
            instance_id=instance_id,
        )

        job.additional_properties = d
        return job

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
