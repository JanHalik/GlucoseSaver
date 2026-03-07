
import httpx
import asyncio
import threading
import os
from shared.enums.general import WSOperation, EntityName
VIEWER_URL = os.getenv("VIEWER_URL")  # port viewer app
if not VIEWER_URL:
    raise RuntimeError("Environment variable VIEWER_URL must be set.")
def WS_notify_service(operation: WSOperation, entity_id: int, tenant_id: str, aditional_id:str=None):
    async def _send():
        try:
            if aditional_id:
                log.warning(f"Viewer notification: {operation.value}/{EntityName.SERVICE.value}/{entity_id}/{tenant_id}/{aditional_id}")
                url = f"{VIEWER_URL}/{operation.value}/{EntityName.SERVICE.value}/{entity_id}/{tenant_id}/{aditional_id}"
            else:
                log.warning(f"Viewer notification: {operation.value}/{EntityName.SERVICE.value}/{entity_id}/{tenant_id}")
                url = f"{VIEWER_URL}/{operation.value}/{EntityName.SERVICE.value}/{entity_id}/{tenant_id}"
            async with httpx.AsyncClient(timeout=2) as client:
                await client.post(url)
        except Exception as e:
            log.warning(f"Viewer notification skipped: {e}")

    try:
        # Pokud běží event loop (FastAPI, async funkce)
        loop = asyncio.get_running_loop()
        loop.create_task(_send())
    except RuntimeError:
        # Žádný event loop neběží (sync kód) → pustíme ve vlákně
        def runner():
            asyncio.run(_send())
        threading.Thread(target=runner, daemon=True).start()