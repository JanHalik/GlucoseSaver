import os
import asyncio
from datetime import datetime
from pylibrelinkup import PyLibreLinkUp, APIUrl

EMAIL = "halik.jan@gmail.com"
PASSWORD = "MHDiaObvodova1"

INTERVAL = 600
CSV_FILE = "glucose.csv"


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

    csv_lines = []

    if not os.path.exists(CSV_FILE):
        csv_lines.append("timestamp,glucose,unit")

    try:
        while True:
            try:
                data = await fetch_latest(client, patient_id)

                timestamp = data.timestamp
                value = data.value

                print(f"{timestamp} -> {value} mol/l")
                csv_lines.append(f"{timestamp},{value},mol/l")

            except Exception as e:
                print(
                    f"[{datetime.now().isoformat(timespec='seconds')}] Chyba: {e}"
                )

            await asyncio.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Ukončení pomocí Ctrl+C")

    finally:
        await asyncio.to_thread(write_csv, csv_lines)
        print(f"CSV uloženo do souboru: {CSV_FILE}")


def write_csv(lines):
    with open(CSV_FILE, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


if __name__ == "__main__":
    asyncio.run(main())