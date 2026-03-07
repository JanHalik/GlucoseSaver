import asyncio
from datetime import datetime, timedelta

import email
import os, logging
import signal
import sys
import asyncio
from datetime import datetime
from pylibrelinkup import PyLibreLinkUp, APIUrl

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


class ClientWorker:
    def __init__(self, email, password, api_url):
        self.email = email
        self.password = password
        self.api_url = api_url
        self.client = None
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

    async def add_client(self, email, password, api_url):
        if email in self.workers:
            print(f"Klient {email} již běží.")
            return

        worker = ClientWorker(email, password, api_url)
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
            url = f"{VIEWER_URL}/view/websocket/notify/{operation.value}/{EntityName.GLUCOSE.value}/{patient_id}"
            glucose = Glucose(value=value, timestamp=datetime)
            async with httpx.AsyncClient(timeout=2) as client:
                await client.post(url, json=glucose.model_dump_json())
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


async def main():
    manager = ClientManager()
    # počáteční klient
    await manager.add_client(EMAIL, PASSWORD, APIUrl.EU)

    # aplikace běží dál a můžeš dynamicky přidávat klienty
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())