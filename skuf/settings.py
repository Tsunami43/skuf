"""
Settings module - backward compatibility shim.

This file is kept for backward compatibility.
The actual implementation is now in skuf.settings_module package.
"""

from skuf.settings_module import BaseSettings

__all__ = ["BaseSettings"]
