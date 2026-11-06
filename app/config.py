from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Business Intelligence AI"
    database_url: str = "sqlite:///./data/business.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 5
    upload_dir: str = "./data/uploads"
    index_dir: str = "./data/index"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
