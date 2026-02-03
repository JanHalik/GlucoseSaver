import time
from datetime import datetime
from pylibrelinkup import PyLibreLinkUp


# Přihlašovací údaje
EMAIL = "halik.jan@gmail.com"
PASSWORD = "MHDiaObvodova1"

# Interval v sekundách (10 minut)
INTERVAL = 600

def main():
    client = PyLibreLinkUp(email=EMAIL, password=PASSWORD)
    client.authenticate()

    patients = client.get_patients()
    if not patients:
        raise RuntimeError("Žádní pacienti nejsou propojeni s účtem.")

    patient_id = patients[0].patient_id 

    print(f"Sleduji pacienta: {patients[0].first_name} {patients[0].last_name}")

    while True:
        try:
            data = client.latest(patient_identifier=patient_id)
            print(data)

            now = datetime.now().isoformat(timespec="seconds")

            print(
                f"[{now}] Glukóza: {data} mmol/l"
            )

        except Exception as e:
            print(f"[{datetime.now().isoformat(timespec='seconds')}] Chyba: {e}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
