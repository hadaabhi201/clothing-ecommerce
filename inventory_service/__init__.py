"""
Inventory Service package.
Expose app factory and common version info here if needed.
"""

__version__ = "0.1.0"

# Optional convenience export
from .main import app  # noqa: F401

__all__ = ["app", "__version__"]
