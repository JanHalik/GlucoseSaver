import os
import signal
import sys
import asyncio
from datetime import datetime
from pylibrelinkup import PyLibreLinkUp, APIUrl

EMAIL = "halik.jan@gmail.com"
PASSWORD = "MHDiaObvodova1"

INTERVAL = 600

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


async def main():
    client = PyLibreLinkUp(
        email=EMAIL,
        password=PASSWORD,
        api_url=APIUrl.EU
    )

    await authenticate(client)

    patients = await get_patients(client)
    if not patients:
        raise RuntimeError("Žádní pacienti nejsou propojeni s účtem.")

    patient = patients[0]
    patient_id = patient.patient_id

    print(f"Sleduji pacienta: {patient.first_name} {patient.last_name}")

    try:
        while True:
            try:
                data = await fetch_latest(client, patient_id)

                timestamp = data.timestamp
                value = data.value

                csv_line=f"{timestamp},{value},mol/l"
                print(csv_line)
                await asyncio.to_thread(write_csv, csv_line,f"{patient.first_name}_{patient.last_name}")
            except Exception as e:
                print(
                    f"[{datetime.now().isoformat(timespec='seconds')}] Chyba: {e}"
                )

            await asyncio.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Ukončení pomocí Ctrl+C")

def get_csv_file(patient):
    """Vrátí název souboru pro dnešní den"""
    day_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/{day_prefix}_{patient}_glucose.csv"
    return filename
def write_csv(line,patient):
    csv_file = get_csv_file(patient)
    # pokud soubor ještě neexistuje, přidej hlavičku
    if not os.path.exists(csv_file):
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("timestamp,glucose,unit\n")
    # zapis datový řádek
    with open(csv_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

if __name__ == "__main__":
    asyncio.run(main())