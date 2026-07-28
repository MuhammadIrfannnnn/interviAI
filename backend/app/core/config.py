from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    API_PREFIX: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    LLM_PROVIDER:str
    GEMINI_API_KEY:str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()