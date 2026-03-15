# manager.py
from fastapi import WebSocket
from typing import List
import asyncio
from datetime import datetime, timezone
# Správa připojených klientů
import os,logging,sys
log = logging.getLogger("viewer")
log.setLevel(logging.DEBUG)
# handler zapisující do stdout
handler = logging.StreamHandler(sys.stdout)
# přidání handleru k loggeru
log.addHandler(handler)
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        # runs paralel running task on background
        asyncio.create_task(self.monitor_connections())

    async def connect(self, websocket: WebSocket, patient_id: str):
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        if websocket in self.active_connections[patient_id]:
            log.info(f"Websocket already connected for patient {patient_id}")
            return
        log.info(f"Add ws connection for patient {patient_id}")
        self.active_connections[patient_id].append(websocket)

    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.active_connections:
            self.active_connections[patient_id] = [
                ws for ws in self.active_connections[patient_id]
                if ws != websocket
            ]
            if not self.active_connections[patient_id]:
                # remove the key if no sockets left for this patient_id
                del self.active_connections[patient_id]

    async def broadcast(self, message: dict, patient_id: str):
        if patient_id in self.active_connections:
            for ws in self.active_connections[patient_id]:
                log.info(f"Send datat to WS {patient_id}: {message}")
                await ws.send_json(message)
    def has_patient_connection(self, patient_id):
        return self.active_connections.get(patient_id)


    async def monitor_connections(self):
        while True:
            now = datetime.now(timezone.utc)
            log.info(f"Test active connections: {now}")
            for patient_id, sockets in list(self.active_connections.items()):
                log.info(f"Test connection: {patient_id} - {len(sockets)} sockets")
            await asyncio.sleep(300)  # check every 30s