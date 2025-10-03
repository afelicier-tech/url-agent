# config.py
from pydantic import BaseModel

class Settings(BaseModel):
    # concurrency
    max_concurrency: int = 30
    request_timeout_seconds: int = 20
    user_agent: str = "AgenticURLChecker/1.0"

    # storage
    use_snowflake: bool = False

    # human-in-loop
    review_threshold_status_codes: tuple = (400, 499, 500, 599)

    class Config:
        env_file = ".env"

settings = Settings()
