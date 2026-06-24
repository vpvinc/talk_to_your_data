import os

from pandasai import Agent
from pandasai.data_loader.loader import DatasetLoader
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.llm.openai import OpenAI

from talk_to_your_data.intake import IntakeMessage
from talk_to_your_data.semantic_layer import SCHEMAS

# Directory used by PandasAI loaders for query caching and metadata
_DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")


def _build_agent() -> Agent:
    """Instantiate VirtualDataFrames from the semantic layer and return a PandasAI Agent."""
    llm = OpenAI(api_token=os.environ["OPENAI_API_KEY"])
    vdfs = [
        VirtualDataFrame(data_loader=DatasetLoader.create_loader_from_schema(schema, _DATASETS_DIR))
        for schema in SCHEMAS
    ]
    return Agent(vdfs, config={"llm": llm})


_agent = _build_agent()


def process(message: IntakeMessage) -> str:
    """Run the user's question through PandasAI and return a plain-text answer."""
    result = _agent.chat(message.text)
    return str(result)
