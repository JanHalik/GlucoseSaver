import os
import time
from datetime import datetime
from pylibrelinkup import PyLibreLinkUp


# Přihlašovací údaje
EMAIL = "halik.jan@gmail.com"
PASSWORD = "MHDiaObvodova1"

# Interval v sekundách (10 minut)
INTERVAL = 600
CSV_FILE = "glucose.csv"
def main():
    client = PyLibreLinkUp(email=EMAIL, password=PASSWORD)
    client.authenticate()

    patients = client.get_patients()
    if not patients:
        raise RuntimeError("Žádní pacienti nejsou propojeni s účtem.")

    patient_id = patients[0].patient_id 

    print(f"Sleduji pacienta: {patients[0].first_name} {patients[0].last_name}")
    csv=[]
    # 1️⃣ Načtení existujícího CSV při startu
    if not os.path.exists(CSV_FILE):
        # with open(CSV_FILE, "r", encoding="utf-8") as f:
        #     csv = [line.strip() for line in f if line.strip()]
    #else:
        # hlavička – zapíše se jen při prvním spuštění
        csv.append("timestamp,glucose,unit")
    try:
        while True:
            try:
                data = client.latest(patient_identifier=patient_id)
                print(data)

                now = datetime.now().isoformat(timespec="seconds")

                print(f"{data},mol/l")
                timestamp=data.timestamp
                value=data.value
                csv.append(f"{timestamp},{value},mol/l")

            except Exception as e:
                print(f"[{datetime.now().isoformat(timespec='seconds')}] Chyba: {e}")

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Ukončení pomocí Ctrl+C")

    finally:
        with open(CSV_FILE, "a", encoding="utf-8") as f:
            for line in csv:
                f.write(line + "\n")

        print(f"CSV uloženo do souboru: {CSV_FILE}")



if __name__ == "__main__":
    main()
