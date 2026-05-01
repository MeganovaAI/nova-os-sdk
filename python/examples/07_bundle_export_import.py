"""Bundle export / import — tenant onboarding round-trip.

Nova OS employee bundles (``*.nova-bundle.zip``) let you snapshot a fully
configured employee (model config, owned agents, custom tools, persona
prompt) from one Nova OS instance and import it into another. This is the
primary tenant onboarding mechanism for multi-tenant deployments.

The export endpoint returns raw ZIP bytes. The import endpoint accepts the
same bytes. There is no resource-level helper yet (``c.employees.export_bundle()``
is planned for a future release); this example uses ``c._http`` to call the
bundle endpoints directly.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_SRC_URL=https://nova-source.partner.com
    export NOVA_OS_DST_URL=https://nova-dest.partner.com
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 07_bundle_export_import.py
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from nova_os import Client


async def main() -> None:
    api_key = os.environ["NOVA_OS_API_KEY"]
    src_url = os.environ.get("NOVA_OS_SRC_URL", os.environ.get("NOVA_OS_URL", "https://nova.partner.com"))
    dst_url = os.environ.get("NOVA_OS_DST_URL", os.environ.get("NOVA_OS_URL", "https://nova.partner.com"))
    employee_id = os.environ.get("NOVA_OS_EMPLOYEE_ID", "frontdesk")

    # --- Export ---
    async with Client(base_url=src_url, api_key=api_key) as src:
        # c.employees.export_bundle() is planned for a future SDK release.
        # Until then, call the endpoint directly via the underlying httpx client.
        #
        # GET /v1/managed/employees/{id}/bundle  →  application/zip bytes
        resp = await src._http.get(
            f"/v1/managed/employees/{employee_id}/bundle",
            headers={"Accept": "application/zip"},
        )
        resp.raise_for_status()
        bundle_bytes: bytes = resp.content
        print(f"Exported bundle: {len(bundle_bytes):,} bytes from {employee_id}@{src_url}")

    # Optionally persist the bundle to disk for audit / version control.
    with tempfile.NamedTemporaryFile(suffix=".nova-bundle.zip", delete=False) as tmp:
        tmp.write(bundle_bytes)
        bundle_path = Path(tmp.name)
    print(f"Saved to: {bundle_path}")

    # --- Import ---
    async with Client(base_url=dst_url, api_key=api_key) as dst:
        # POST /v1/managed/employees/import  →  application/zip body
        import_resp = await dst._http.post(
            "/v1/managed/employees/import",
            content=bundle_bytes,
            headers={
                "Content-Type": "application/zip",
                # on_conflict=overwrite replaces an existing employee with the same ID.
                "X-Nova-On-Conflict": "overwrite",
            },
        )
        import_resp.raise_for_status()
        result = import_resp.json()
        print(f"Imported bundle: {result}")

    # Clean up the temp file.
    bundle_path.unlink(missing_ok=True)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
