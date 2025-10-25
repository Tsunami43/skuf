from typing import Any, List

__all__ = ["Parser"]


class Parser:
    """Parser for converting environment variable strings to typed values."""
    
    @staticmethod
    def parse(raw_value: str, typ: Any) -> Any:
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
            parts = [p.strip() for p in raw_value.split(",")]
            if subtype is int:
                return [int(p) for p in parts if p.lstrip("-").isdigit()]
            if subtype is float:
                return [float(p) for p in parts]
            return parts  # List[str]

        if typ is str:
            return raw_value

        return raw_value  # fallback for unsupported types
