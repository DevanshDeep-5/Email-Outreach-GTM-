from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    openrouter_api_key: str
    people_data_labs_api_key: str
    firecrawl_api_key: str
    tavily_api_key: str

    model_config = {"env_file": ".env"}


settings = Settings()
