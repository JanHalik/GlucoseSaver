# manager.py
from fastapi import WebSocket
from typing import List
import asyncio
from datetime import datetime, timezone
# Správa připojených klientů
import os,logging
log = logging.getLogger("viewer")
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[(str,WebSocket)]] = {}
        # runs paralel running task on background
        asyncio.create_task(self.monitor_connections())

    async def connect(self, websocket: WebSocket, patient_id: str, token:str):
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        self.active_connections[patient_id].append((token,websocket))

    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.active_connections:
            self.active_connections[patient_id] = [
                (t, ws) for (t, ws) in self.active_connections[patient_id]
                if ws != websocket
            ]
            if not self.active_connections[patient_id]:
                # remove the key if no sockets left for this patient_id
                del self.active_connections[patient_id]

    async def broadcast(self, message: dict, patient_id: str):
        if patient_id in self.active_connections:
            for (token,ws) in self.active_connections[patient_id]:
                log.info(f"Send datat to WS {patient_id}: {message}")
                await ws.send_json(message)
    def has_patient_connection(self, patient_id):
        return self.active_connections.get(patient_id)


    async def monitor_connections(self):
        while True:
            now = datetime.now(timezone.utc)
            log.info(f"Test active connections: {now}")
            await asyncio.sleep(300)  # check every 30s