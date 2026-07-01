import os

import yaml
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    Relation,
    SemanticLayerSchema,
    Source,
    SQLConnectionConfig,
)

_db_config = SQLConnectionConfig(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
)

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "schema_config.yaml")


def _load_schemas() -> list[SemanticLayerSchema]:
    with open(_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    schemas = []
    for t in config["tables"]:
        db_schema = t.get("db_schema", "public")
        table = t["table"]
        full_table = f"{db_schema}.{table}" if db_schema != "public" else table

        raw_relations = t.get("relations", [])
        relations = [Relation.model_validate(r) for r in raw_relations] if raw_relations else None

        schemas.append(SemanticLayerSchema(
            name=t["name"],
            description=t["description"],
            source=Source(type="postgres", connection=_db_config, table=full_table),
            columns=[Column(**c) for c in t["columns"]],
            relations=relations,
        ))

    return schemas


# The engine imports this list — add new tables in schema_config.yaml.
SCHEMAS: list[SemanticLayerSchema] = _load_schemas()
