"""Base configuration class for agents."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import colorlog


class BaseConfig:
    """Base configuration class with common settings."""

    def __init__(self, config_dir_path: Path) -> None:
        """
        Initialize config.

        Args:
            config_dir_path: Path to the directory containing .env file (usually Path(__file__).parent)

        Raises:
            ValueError: If config_dir_path does not exist
        """
        if not config_dir_path.exists():
            raise ValueError(f"Config directory not found: {config_dir_path}")

        if not config_dir_path.is_dir():
            raise ValueError(f"Config path is not a directory: {config_dir_path}")

        env_file = config_dir_path / ".env"

        if env_file.exists():
            load_dotenv(env_file)
        else:
            logging.debug(f"No .env file found at {env_file}, using environment variables")
        # self.config = dict(os.environ)


        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_colors: bool = os.getenv("LOG_COLORS", "true").lower() == "true"
        self.system_prompt_path: str | None = os.getenv("SYSTEM_PROMPT_PATH")
        self.config_dir: Path = config_dir_path

    def load_system_prompt(self, default_filename: str = "system_prompt.md") -> str:
        """Load system prompt from file.

        Args:
            default_filename: Default filename to use if SYSTEM_PROMPT_PATH not set

        Returns:
            Content of the system prompt file, or empty string if not found
        """
        if self.system_prompt_path:
            prompt_path = self.config_dir / self.system_prompt_path
        else:
            prompt_path = self.config_dir / default_filename
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging.warning(f"System prompt file not found at {prompt_path}")
            return ""

    def setup_logging(self, logger_name: str = "strands") -> None:
        """Setup logging with the provided configuration.

        Args:
            logger_name: Name of the logger to configure
        """
        logging.getLogger(logger_name).setLevel(getattr(logging, self.log_level.upper()))

        handler = colorlog.StreamHandler()
        log_format = "%(log_color)s%(levelname)s%(reset)s | %(name)s | %(message)s"

        if self.log_colors:
            handler.setFormatter(colorlog.ColoredFormatter(log_format))
        else:
            plain_format = log_format.replace("%(log_color)s", "").replace("%(reset)s", "")
            handler.setFormatter(logging.Formatter(plain_format))

        logging.basicConfig(handlers=[handler], level=getattr(logging, self.log_level.upper()))
