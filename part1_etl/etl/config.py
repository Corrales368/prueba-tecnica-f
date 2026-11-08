import os

ERP_BASE_URL = os.environ["ERP_BASE_URL"]
ERP_USER = os.environ["ERP_USER"]
ERP_PASSWORD = os.environ["ERP_PASSWORD"]
DATABASE_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ['POSTGRES_HOST']}:5432/{os.environ['POSTGRES_DB']}"
)
WORKERS = int(os.environ.get("ETL_WORKERS", 5))
