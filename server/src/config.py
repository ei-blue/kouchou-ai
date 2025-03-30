import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

Environment = Literal["development", "production"]


class Settings(BaseSettings):
    ADMIN_API_KEY: str = Field(env="ADMIN_API_KEY")
    PUBLIC_API_KEY: str = Field(env="PUBLIC_API_KEY")
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    ENVIRONMENT: Environment = Field(env="ENVIRONMENT", default="production")
    BASE_DIR: Path = Path(__file__).parent.parent
    TOOL_DIR: Path = BASE_DIR / "broadlistening"
    REPORT_DIR: Path = TOOL_DIR / "pipeline" / "outputs"
    CONFIG_DIR: Path = TOOL_DIR / "pipeline" / "configs"
    INPUT_DIR: Path = TOOL_DIR / "pipeline" / "inputs"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Azure OpenAI Service configuration
    USE_AZURE: bool = Field(env="USE_AZURE", default=False)
    ## for ChatCompletiion
    AZURE_CHATCOMPLETION_ENDPOINT: str = Field(env="AZURE_CHATCOMPLETION_ENDPOINT", default="https://kouchou-ai-openai.openai.azure.com")
    AZURE_CHATCOMPLETION_DEPLOYMENT_NAME: str = Field(env="AZURE_CHATCOMPLETION_DEPLOYMENT_NAME", default="gpt4o")
    AZURE_CHATCOMPLETION_VERSION: str = Field(env="AZURE_CHATCOMPLETION_VERSION", default="2024-10-21")
    AZURE_CHATCOMPLETION_API_KEY: str = Field(env="AZURE_CHATCOMPLETION_API_KEY", default="*****")
    ## for Embedding
    AZURE_EMBEDDING_ENDPOINT: str = Field(env="AZURE_EMBEDDING_ENDPOINT", default="https://kouchou-ai-openai.openai.azure.com")
    AZURE_EMBEDDING_DEPLOYMENT_NAME: str = Field(env="AZURE_EMBEDDING_DEPLOYMENT_NAME", default="text-embedding-3-large")
    AZURE_EMBEDDING_VERSION: str = Field(env="AZURE_EMBEDDING_VERSION", default="2023-05-15")
    AZURE_EMBEDDING_API_KEY: str = Field(env="AZURE_EMBEDDING_API_KEY", default="*****")
    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env.server")


settings = Settings()
# レポート出力ツール側でOpenAI APIを利用できるように、環境変数にセットする
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
