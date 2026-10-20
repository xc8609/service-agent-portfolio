import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    database_url: str = field(repr=False)
    mode: str = "local"
    provider_config: str | None = field(default=None, repr=False)

    def __post_init__(self):
        if self.mode != "local":
            raise ValueError("Only local synthetic demo mode is supported")
        if not self.database_url.startswith(("postgresql://", "postgres://")):
            raise ValueError("A PostgreSQL runtime connection is required")

    @classmethod
    def from_env(cls):
        return cls(
            os.environ.get("BANK_DATABASE_URL", ""),
            os.environ.get("BANK_MODE", "local"),
            os.environ.get("BANK_PROVIDER_CONFIG") or None,
        )
