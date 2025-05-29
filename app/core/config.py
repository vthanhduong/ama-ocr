from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    API_VERSION: str
    OPENAI_API_KEY: str
    DATABASE_URL: str
    AZURE_RESOURCE_ENDPOINT: str
    AZURE_RESOURCE_API_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    model_config=SettingsConfigDict(env_file='.env')
    
settings = Settings()