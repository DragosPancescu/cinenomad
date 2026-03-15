import logging

from utils.file_handling import load_yaml_file
from .sqlite_handler import SQLiteHandler


def setup_logging(config_path: str) -> None:
    """Configures the root logger with stdout and SQLite handlers.

    Args:
        config_path (str): Path to the logging configuration YAML file
    """
    config = load_yaml_file(config_path)

    log_format = config.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    date_format = config.get("date_format", "%Y-%m-%d %H:%M:%S")
    root_level = config.get("root_level", "DEBUG")
    stdout_level = config.get("stdout_level", "DEBUG")
    sqlite_level = config.get("sqlite_level", "DEBUG")

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Stdout handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(getattr(logging, stdout_level))
    stdout_handler.setFormatter(formatter)

    # SQLite handler
    sqlite_handler = SQLiteHandler()
    sqlite_handler.setLevel(getattr(logging, sqlite_level))
    sqlite_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, root_level))
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(sqlite_handler)

    # Apply per-logger level overrides
    logger_overrides = config.get("logger_overrides", {})
    for logger_name, level in logger_overrides.items():
        logging.getLogger(logger_name).setLevel(getattr(logging, level))
