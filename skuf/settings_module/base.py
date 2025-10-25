import os
from typing import Any, get_type_hints

from .parser import Parser
from .loader import Loader

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
    - List[int], List[float], List[str] (comma-separated: "1,2,3")

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
        Loader.load_env(self.__class__.__path_env__)
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
                if raw_value is None or raw_value.strip() == "":
                    raise AttributeError(f"Environment variable {env_name} is not set.")
                value = Parser.parse(raw_value, self._types[name])
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
