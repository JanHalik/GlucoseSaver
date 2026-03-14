import asyncio
from datetime import datetime, timedelta, timezone

import email
import os, logging
import signal
import sys
import asyncio
from datetime import datetime
from pylibrelinkup import PyLibreLinkUp, APIUrl
import requests
from glucose_viewer import manager
from glucose_viewer.schemas.glucose import Glucose
from shared.enums.general import WSOperation, EntityName
import httpx
import threading
EMAIL = "halik.jan@gmail.com"
PASSWORD = "MHDiaObvodova1"


def handle_sigterm(signum, frame):
    print("Service Glucose is stopping...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
async def fetch_latest(client, patient_id):
    return await asyncio.to_thread(
        client.latest, patient_identifier=patient_id
    )


async def authenticate(client):
    await asyncio.to_thread(client.authenticate)


async def get_patients(client):
    return await asyncio.to_thread(client.get_patients)

PATIENT_REFRESH_INTERVAL = 60 * 60 * 2  # 2 hodiny
INTERVAL = 600  # interval měření

polled_patients: dict[str, PyLibreLinkUp] = {}


class ClientWorker:
    def __init__(self, email, password, api_url, client_id):
        self.email = email
        self.password = password
        self.api_url = api_url
        self.client = None
        self.client_id = client_id
        self.patients = []
        self.last_patient_refresh = None
        self.running = True

    async def setup(self):
        self.client = PyLibreLinkUp(
            email=self.email,
            password=self.password,
            api_url=self.api_url
        )
        await authenticate(self.client)
        await self.refresh_patients()

    async def refresh_patients(self):
        try:
            patients = await get_patients(self.client)
            self.patients = patients or []
            self.last_patient_refresh = datetime.utcnow()

            if not self.patients:
                print(f"[{self.email}] Žádní pacienti.")
            else:
                patients=getPatients(self.client_id)
            # add missing patients
            for patient in self.patients:
                if not any(p["id"] == str(patient.patient_id) for p in patients):
                    breakpoint()
                    addPatient(self.client_id, patient.first_name, patient.last_name, str(patient.patient_id))
            # filter patients to those with active poller state
            patients=getPatients(self.client_id)
            self.patients = [p for p in self.patients if not any(p["id"] == str(patient.patient_id) and p["PollerState"] == "active" for p in patients)]
            breakpoint()
        except Exception as e:
            print(f"[{self.email}] Chyba při načítání pacientů: {e}")

    async def run(self):
        await self.setup()

        while self.running:
            try:
                # refresh pacientů každé 2 hodiny
                if (
                    not self.last_patient_refresh
                    or datetime.utcnow() - self.last_patient_refresh
                    > timedelta(seconds=PATIENT_REFRESH_INTERVAL)
                ):
                    await self.refresh_patients()

                if not self.patients:
                    await asyncio.sleep(INTERVAL)
                    continue

                for patient in self.patients:
                    try:
                        data = await fetch_latest(self.client, patient.patient_id)

                        timestamp = data.timestamp
                        value = data.value

                        csv_line = f"{timestamp},{value},mol/l"
                        print(f"[{self.email}] {csv_line}")

                        await asyncio.to_thread(write_csv, timestamp, value, patient.patient_id, f"{patient.first_name}_{patient.last_name}")
                    except Exception as e:
                        print(
                            f"[{self.email}] "
                            f"[{datetime.utcnow().isoformat(timespec='seconds')}] "
                            f"Chyba pacienta {patient.patient_id}: {e}"
                        )

            except Exception as e:
                print(f"[{self.email}] Kritická chyba smyčky: {e}")

            await asyncio.sleep(INTERVAL)


class ClientManager:
    def __init__(self):
        self.workers = {}

    async def add_client(self, email, password, api_url, client_id):
        if email in self.workers:
            print(f"Klient {email} již běží.")
            return

        worker = ClientWorker(email, password, api_url, client_id)
        task = asyncio.create_task(worker.run())

        self.workers[email] = {
            "worker": worker,
            "task": task,
        }

        print(f"Přidán klient {email}")

    async def remove_client(self, email):
        entry = self.workers.get(email)
        if not entry:
            return

        entry["worker"].running = False
        entry["task"].cancel()
        del self.workers[email]

        print(f"Odebrán klient {email}")

def get_csv_file(patient):
    """Vrátí název souboru pro dnešní den"""
    day_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/{day_prefix}_{patient}_glucose.csv"
    return filename
def write_csv(timestamp,value,patient_id,patient_name):
    csv_file = get_csv_file(patient_name)
    # pokud soubor ještě neexistuje, přidej hlavičku
    if not os.path.exists(csv_file):
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("timestamp,glucose,unit\n")
    # zapis datový řádek
    with open(csv_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp},{value},mol/l" + "\n")
    # notify websocket clients about new data
    WS_notify_service(WSOperation.ADD, patient_id, timestamp, value)  # entity_id není relevantní, použijeme 0

VIEWER_URL = os.getenv("VIEWER_URL","http://localhost:8088")  # port viewer app
if not VIEWER_URL:
    raise RuntimeError("Environment variable VIEWER_URL must be set.")
def WS_notify_service(operation: WSOperation, patient_id: int, datetime: datetime = None, value: float = None):
    async def _send():
        try:
            logging.log(msg=f"Viewer notification: {operation.value}/{EntityName.GLUCOSE.value}/{patient_id}",level=logging.INFO)
            #url = f"{VIEWER_URL}/view/websocket/notify/{operation.value}/{EntityName.GLUCOSE.value}/{patient_id}"
            url = f"{VIEWER_URL}/measurements"


            glucose = Glucose(PatientID=str(patient_id), Value=value, Time=datetime.isoformat(timespec="milliseconds")+"Z")
            logging.log(msg=f"Notification payload: {glucose}", level=logging.INFO)
            async with httpx.AsyncClient(timeout=2) as client:
                await client.post(url, json=glucose.model_dump(mode="json"), headers={"Content-Type": "application/json", "Accept": "application/json"})
        except Exception as e:
            logging.log(msg=f"Viewer notification skipped: {e}",level=logging.ERROR)

    try:
        # Pokud běží event loop (FastAPI, async funkce)
        loop = asyncio.get_running_loop()
        loop.create_task(_send())
    except RuntimeError:
        # Žádný event loop neběží (sync kód) → pustíme ve vlákně
        def runner():
            asyncio.run(_send())
        threading.Thread(target=runner, daemon=True).start()

async def addMeasurement(patient_id: str, timestamp: datetime, value: float):
    url = f"{VIEWER_URL}/measurements"
    glucose = Glucose(PatientID=str(patient_id), Value=value, Time=timestamp.isoformat(timespec="milliseconds")+"Z")
    logging.log(msg=f"Notification payload: {glucose}", level=logging.INFO)
    async with httpx.AsyncClient(timeout=2) as client:
        await client.post(url, json=glucose.model_dump(mode="json"), headers={"Content-Type": "application/json", "Accept": "application/json"})


def getClients():
    try:
        url = f"{VIEWER_URL}/clients"
        response=requests.get(url, headers={"Content-Type": "application/json", "Accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.log(msg=f"Viewer notification skipped: {e}",level=logging.ERROR)
def getPatients(clientId)->str:
    try:
        url = f"{VIEWER_URL}/clients/{clientId}/patients"
        response=requests.get(url, headers={"Content-Type": "application/json", "Accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.log(msg=f"Viewer notification skipped: {e}",level=logging.ERROR)
def deleteRelation(clientId, patientId)->str:
    try:
        url = f"{VIEWER_URL}/client-patient/{clientId}/{patientId}"
        response=requests.delete(url, headers={"Content-Type": "application/json", "Accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.log(msg=f"Viewer notification skipped: {e}",level=logging.ERROR)
def addPatient(clientId,first_name,last_name, id)->str:
    try:
        #If Patient already exist then update with activate state else create new patient with active state and relation to client
        url = f"{VIEWER_URL}/patients/{id}"
        response=requests.get(url, headers={"Content-Type": "application/json", "Accept": "application/json"})
        breakpoint()
        if response.status_code == 200:
            patient=response.json()
            if patient["PollerState"]!="active":
                url = f"{VIEWER_URL}/patients/{id}"
                payload = {
                    "FirstName": first_name,
                    "LastName": last_name,
                    "id": id,
                    "PollerState": "active"
                }
                response=requests.put(url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})
                response.raise_for_status()
            else:
                logging.log(msg=f"Patient {id} already active", level=logging.INFO)
        else:
            url = f"{VIEWER_URL}/patients"
            payload = {
                "FirstName": first_name,
                "LastName": last_name,
                "id": id,
                "PollerState": "active"
            }
            response=requests.post(url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})
            response.raise_for_status()
        # create client-patient relation
        url = f"{VIEWER_URL}/client-patient"
        payload = {
            "ClientID": clientId,
            "PatientID": id
        }
        response=requests.post(url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.log(msg=f"Viewer notification skipped: {e}",level=logging.ERROR)

async def polling_task():
    while True:

        for patient_id, client in polled_patients.items():

            print(f"Polling patient {patient_id} for clients {client}")

            try:
                data = await fetch_latest(client, patient_id)
                timestamp = data.timestamp
                value = data.value

                csv_line = f"{timestamp},{value},mol/l"
                print(f"[{client.email}] {csv_line}")

                await addMeasurement(patient_id, timestamp, value)
            except Exception as e:
                print(
                    f"[{client.email}] "
                    f"[{timestamp.utcnow().isoformat(timespec='seconds')}] "
                    f"Chyba pacienta {patient_id}: {e}"
                )

        await asyncio.sleep(INTERVAL)

async def refresh_patients_task():
    while True:
        clients=getClients()
        for client in clients:
            libre_client = await loginClient(client["Email"],client["Password"])
            patients = await get_patients(libre_client)
            libre_patients_id_list=[str(patient.patient_id) for patient in patients]
            db_patients_id_list=[patient["id"] for patient in getPatients(client["id"])]
            for patient in patients:
                #Activate polling for patient if not already running
                if patient.patient_id not in polled_patients:
                    polled_patients[patient.patient_id] = libre_client
                    print(f"Added patient {patient.patient_id} to polling list.")
                #TODO Compare patients in DB if exist add client-patient connection and if patient does not exist then create
                if str(patient.patient_id) not in db_patients_id_list:
                    addPatient(client["id"],patient.first_name,patient.last_name, str(patient.patient_id))

            # Compare patients in DB if missing remove client-patient connection
            connections_to_remove=set(db_patients_id_list) - set(libre_patients_id_list)
            for patient_id in connections_to_remove:
                #TODO remove client-patient connection and remove patient from polled_patients and set polling as inactive
                polled_patients.pop(patient_id, None)
                deleteRelation(client["id"], patient_id)
                print(f"Patient {patient_id} is missing in LibreLinkUp client {client['FirstName']} {client['LastName']}")


        await asyncio.sleep(PATIENT_REFRESH_INTERVAL)
async def loginClient(email,password)->PyLibreLinkUp:
    client = PyLibreLinkUp(
        email=email,
        password=password,
        api_url=APIUrl.EU
    )
    await authenticate(client)
    return client

async def main():
    await asyncio.gather(
        polling_task(),
        refresh_patients_task()
    )
    # manager = ClientManager()
    # # počáteční klient
    # await manager.add_client(EMAIL, PASSWORD, APIUrl.EU,1)

    # # aplikace běží dál a můžeš dynamicky přidávat klienty
    # while True:
    #     await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())