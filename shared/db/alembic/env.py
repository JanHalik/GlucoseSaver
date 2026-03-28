import os, sys
from sqlalchemy import create_engine
from alembic import context

# přidej parent složku do sys.path, aby šel najít db.models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from shared.db.model import Base
from glucose_viewer.db.db import DATABASE_URL

# DB_USER = os.getenv("DPDB_USER")
# if not DB_USER:
#     raise RuntimeError("Environment variable DPDB_USER must be set.")
# DB_PASS = os.getenv("DPDB_PASSWORD")
# if not DB_PASS:
#     raise RuntimeError("Environment variable DPDB_PASSWORD must be set.")
# DB_HOST = os.getenv("DPDB_HOST")
# if not DB_HOST:
#     raise RuntimeError("Environment variable DPDB_HOST must be set.")
# DPDB_PORT = os.getenv("DPDB_PORT", "3306")
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DPDB_PORT}/dpdb"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
target_metadata = Base.metadata

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_server_default=True, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()