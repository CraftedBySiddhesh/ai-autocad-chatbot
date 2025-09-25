"""Application configuration management."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

UnitsLiteral = Literal["mm", "in"]


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    default_units: UnitsLiteral = Field(
        default="mm",
        alias="DEFAULT_UNITS",
        description="Default units used when parsing user input.",
    )

    @property
    def DEFAULT_UNITS(self) -> UnitsLiteral:  # noqa: N802 - keep env style attribute
        return self.default_units


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings()


def reload_settings() -> Settings:
    """Force settings to be reloaded from environment variables."""

    get_settings.cache_clear()
    return get_settings()
