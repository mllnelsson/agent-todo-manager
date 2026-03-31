from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    atm_database_url: str

    model_config = SettingsConfigDict(env_file="../.env")


config = Config()
