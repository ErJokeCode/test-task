from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import logging


class Settings(BaseSettings):

    def __init__(self):
        super().__init__(
            _env_file="../.env",
            _env_file_encoding="utf-8",
        )
        self.config_logging()

    def config_logging(self, level=logging.INFO) -> None:
        logging.basicConfig(
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-3d %(levelname)-7s - %(message)s",
        )


settings = Settings()
