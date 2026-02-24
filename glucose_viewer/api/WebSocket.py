from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
from enum import Enum
from glucose_viewer import manager
router = APIRouter(prefix="/view")
import os,logging
log = logging.getLogger("viewer")
class WSOperation(str,Enum):
    CHANGE="change"
    ADD="add"
    DELETE="delete"
class EntityName(str,Enum):
    GLUCOSE="glucose"
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    patient_id = websocket.query_params.get("patient_id")
    log.info(f"Client connected(ws): {websocket.client}")
    await manager.connect(websocket,patient_id)
    log.info(f"AC:{manager.active_connections}")
    try:
        while True:
            # waiting for client message
            data = await websocket.receive_text()
            log.info(f"Message received: {data}")
            # response to client
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket,patient_id)
        log.info(f"Client disconnected: {patient_id}")
class MessageType(str, Enum):
    ENTITY = "entity"
    STATISTICS = "entity_stat"
    ERRORS = "error_count"
    SERVICES_COUNT = "services_count"
# Webhook function for notifiing entity change
async def notify_entity_change(type:MessageType,operation:WSOperation, entity: EntityName,  data:dict, patient_id: str, entity_id: str=None):
    log.info({"type":type,"operation":operation, "entity": entity, "id": entity_id, "data":data})
    await manager.broadcast({"type":type,"operation":operation, "entity": entity, "id": entity_id, "data":data},patient_id)

@router.post(
    "/websocket/notify/{operation}/{entity_name}/{entity_id}/{patient_id}",
    summary="Entity change notification",
    tags=["Websocket"],
)

async def notify_change(
    operation: WSOperation,
    entity_name: EntityName,
    entity_id: int,
    patient_id: str,
    aditional_id: Optional[str] = None,
):
    log.info(f"WS notify: {operation}/{entity_name}/{entity_id}/{patient_id}/{aditional_id}")
    data={}
    #Only if some active WS connection for specific tenant
    if manager.has_patient_connection(patient_id):
        await notify_entity_change(MessageType.STATISTICS,WSOperation.ADD,entity_name, data, patient_id, entity_id)
        return
