import sqlite3
import os

DB_NAME = "Glucose.db"


def init_db():
    db_exists = os.path.exists(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    if not db_exists:

        # APP_USER
        cursor.execute("""
        CREATE TABLE AppUser (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT NOT NULL UNIQUE,
            FirstName TEXT,
            LastName TEXT,
            Email TEXT,
            PhoneNumber TEXT,
            Password TEXT NOT NULL
        );
        """)
        # CLIENT
        cursor.execute("""
        CREATE TABLE Client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Email TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            AppUserID INTEGER NOT NULL,
            FOREIGN KEY (AppUserID)
                REFERENCES AppUser(id)
                ON DELETE CASCADE
        );
        """)

        # PATIENT
        cursor.execute("""
        CREATE TABLE Patient (
            id TEXT PRIMARY KEY,
            FirstName TEXT,
            LastName TEXT,
            PollerState TEXT NOT NULL
            CHECK(PollerState IN ('active','inactive','error'))
            DEFAULT 'inactive'
        );
        """)

        # CLIENT_PATIENT RELATION
        cursor.execute("""
        CREATE TABLE Client_PatientAG (
            idClientPatientAG INTEGER PRIMARY KEY AUTOINCREMENT,
            ClientID INTEGER NOT NULL,
            PatientID TEXT NOT NULL,

            FOREIGN KEY (ClientID)
                REFERENCES Client(id)
                ON DELETE CASCADE,

            FOREIGN KEY (PatientID)
                REFERENCES Patient(id)
                ON DELETE CASCADE
        );
        """)

        # PATIENT DATA
        cursor.execute("""
        CREATE TABLE Patient_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientID TEXT NOT NULL,
            Value REAL NOT NULL,
            Time TEXT NOT NULL,
            Unit TEXT NOT NULL,

            FOREIGN KEY (PatientID)
                REFERENCES Patient(id)
                ON DELETE CASCADE
        );
        """)

        # ---- INDEXES ----

        # relation indexes
        cursor.execute("""
        CREATE INDEX idx_client_patient_client
        ON Client_PatientAG(ClientID);
        """)

        cursor.execute("""
        CREATE INDEX idx_client_patient_patient
        ON Client_PatientAG(PatientID);
        """)

        # patient measurement lookup
        cursor.execute("""
        CREATE UNIQUE INDEX uq_client_patient
        ON Client_PatientAG(ClientID, PatientID);
        """)
        cursor.execute("""
        CREATE INDEX idx_patient_time
        ON Patient_data(PatientID, Time);
        """)
        cursor.execute("""
        CREATE INDEX idx_client_appuser
        ON Client(AppUserId);
        """)
        cursor.execute("""
        CREATE UNIQUE INDEX idx_appuser_login
        ON AppUser(Login);
        """)
        conn.commit()
        print("Glucose database created and initialized.")

    else:
        print("Glucose database already exists.")

    conn.close()


if __name__ == "__main__":
    init_db()