import os
import warnings

__all__ = ["Loader"]


class Loader:
    """Loader for environment variables from .env files."""
    
    @staticmethod
    def load_env(filepath: str) -> None:
        """
        Manually loads environment variables from a .env file if it exists.

        Each line should follow KEY=VALUE format.
        Lines starting with '#' or empty lines are ignored.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = value
        except FileNotFoundError:
            warnings.warn(f".env file {filepath} not found.", stacklevel=1)
