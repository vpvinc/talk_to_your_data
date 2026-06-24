import os

from pandasai.data_loader.semantic_layer_schema import (
    Column,
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

# ---------------------------------------------------------------------------
# Add one SemanticLayerSchema per table below.
# Duplicate the block, set the real table name, description, and columns.
# ---------------------------------------------------------------------------

_example_table = SemanticLayerSchema(
    name="example_table",
    description="Replace this with a real table description.",
    source=Source(type="postgres", connection=_db_config, table="example_table"),
    columns=[
        Column(name="id", type="integer", description="Primary key"),
        # Add more columns here
    ],
)

# The engine imports this list — add your schemas to it.
SCHEMAS: list[SemanticLayerSchema] = [
    _example_table,
]
