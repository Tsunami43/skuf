import os
import warnings
from typing import List, get_type_hints, Any

__all__ = ["BaseSettings"]


class BaseSettings:
    """
    BaseSettings is a lightweight configuration loader that reads environment variables
    and parses them into typed attributes. It supports automatic loading from a `.env` file
    and lazy evaluation of values upon first access.

    Attributes should be declared using type hints in a subclass. The values will be
    automatically retrieved from environment variables (or `.env`) and converted to the proper type.

    Supported types:
    - str
    - int
    - float
    - bool (true, 1, yes, on)
    - List[int], List[float], List[str] (pipe-separated: "1|2|3")

    Example usage:

    ```python
    class Settings(BaseSettings):
        token: str
        retries: int
        timeout: float
        use_cache: bool
        servers: List[str]

    settings = Settings()
    print(settings.token)
    ```

    By default, `.env` is loaded once during initialization if present.
    """

    __path_env__: str = ".env"  # Default .env path, can be overridden per subclass

    def __init__(self):
        """
        Initializes the settings object, loads the .env file, and prepares internal type mappings.
        """
        self._load_env(self.__class__.__path_env__)
        self._values: dict[str, Any] = {}
        self._types = get_type_hints(self.__class__)

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically retrieves a setting value by attribute name.
        Automatically loads and parses the value from environment variables.

        Raises:
            AttributeError: If the variable is not defined or not set in the environment.
        """
        if name in self._types:
            if name not in self._values:
                env_name = name.upper()
                raw_value = os.getenv(env_name)
                if raw_value is None:
                    raise AttributeError(f"Environment variable {env_name} is not set.")
                value = self._parse_value(raw_value, self._types[name])
                self._values[name] = value
            return self._values[name]
        raise AttributeError(f"{name} not found.")

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Overrides attribute setting to store values in the internal cache
        if the attribute is declared as a setting.
        """
        if name in ("_values", "_types") or name not in getattr(self, "_types", {}):
            super().__setattr__(name, value)
        else:
            self._values[name] = value

    def _parse_value(self, raw_value: str, typ: Any) -> Any:
        """
        Parses raw string values from the environment into their declared types.

        Supports:
        - int, float, str, bool
        - List[int], List[float], List[str]
        """
        origin = getattr(typ, "__origin__", None)

        if typ is bool:
            return raw_value.lower() in ("1", "true", "yes", "on")

        if typ is int:
            return int(raw_value)

        if typ is float:
            return float(raw_value)

        if origin in (list, List):
            subtype = typ.__args__[0]
            parts = [p.strip() for p in raw_value.split("|")]
            if subtype is int:
                return [int(p) for p in parts if p.lstrip("-").isdigit()]
            if subtype is float:
                return [float(p) for p in parts]
            return parts  # List[str]

        if typ is str:
            return raw_value

        return raw_value  # fallback for unsupported types

    def _load_env(self, filepath: str) -> None:
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

    def dict(self) -> dict:
        """
        Returns a dictionary of all declared settings and their resolved values.
        Triggers value resolution if needed.
        """
        return {
            name: getattr(self, name)
            for name in self._types
            if not name.startswith("__") and not name.endswith("__")
        }

    def is_loaded(self, name: str) -> bool:
        """
        Checks if a setting has already been resolved and cached.

        Returns:
            bool: True if the value has been accessed or set; False otherwise.
        """
        return name in self._values
