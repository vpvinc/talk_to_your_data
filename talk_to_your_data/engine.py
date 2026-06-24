import os
import shutil
import warnings

import pandas as pd
import pandasai as pai
import pandasai_sql
import psycopg2
from pandasai import Agent
from pandasai_litellm.litellm import LiteLLM

from talk_to_your_data.intake import IntakeMessage
from talk_to_your_data.semantic_layer import SCHEMAS

_DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")

pai.config.set({
    "llm": LiteLLM(model="gpt-4.1-mini"),
    "save_dir": _DATASETS_DIR,
})

_connection = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ["DB_PORT"]),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASS"],
    "database": os.environ["DB_NAME"],
}

# pandasai_sql.load_from_postgres doesn't support schema/search_path.
# Patch it to always include the marts schema so bare table names resolve correctly.
def _load_from_postgres(connection_info, query, params=None):
    conn = psycopg2.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        dbname=connection_info.database,
        port=connection_info.port,
        options="-c search_path=marts,public",
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)

pandasai_sql.load_from_postgres = _load_from_postgres


def _build_agent(refresh: bool = True) -> Agent:
    datasets = []
    for schema in SCHEMAS:
        source_table = schema.source.table  # e.g. "users" or "marts.user_activity_metrics"
        if "." in source_table:
            org, tbl = source_table.split(".", 1)
        else:
            org, tbl = "public", source_table

        path = f"{org}/{tbl.replace('_', '-')}"
        dataset_dir = os.path.join(_DATASETS_DIR, org, tbl.replace("_", "-"))

        if refresh and os.path.exists(dataset_dir):
            shutil.rmtree(dataset_dir)

        if os.path.exists(dataset_dir):
            dataset = pai.load(path)
        else:
            dataset = pai.create(
                path=path,
                description=schema.description,
                source={
                    "type": "postgres",
                    "connection": _connection,
                    "table": tbl,
                },
                columns=[
                    {"name": c.name, "type": c.type, "description": c.description}
                    for c in schema.columns
                ],
            )
        datasets.append(dataset)
    return Agent(datasets)


_agent = _build_agent()


def process(message: IntakeMessage) -> str:
    result = _agent.chat(message.text)
    return str(result)
