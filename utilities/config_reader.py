"""
config_reader.py

Centralized configuration reader.
"""

from __future__ import annotations

import configparser
from pathlib import Path


class ConfigReader:
    """
    Reads values from config/config.ini.

    Configuration is loaded once when the class is initialized.
    """

    _config = configparser.ConfigParser()

    CONFIG_PATH = (
        Path(__file__).resolve().parent.parent
        / "config"
        / "config.ini"
    )

    @classmethod
    def load_config(cls) -> None:
        """Load configuration file."""
        if not cls.CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"Configuration file not found: "
                f"{cls.CONFIG_PATH}"
            )

        cls._config.read(cls.CONFIG_PATH)

    @classmethod
    def get(cls, section: str, key: str) -> str:
        """Return configuration value."""
        if not cls._config.sections():
            cls.load_config()

        if not cls._config.has_option(section, key):
            raise KeyError(
                f"Configuration key '{key}' "
                f"not found in section '{section}'."
            )

        return cls._config.get(section, key)


# Load configuration when module is imported.
ConfigReader.load_config()