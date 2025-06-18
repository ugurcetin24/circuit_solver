"""
Dynamic loader for numerics modules.
Each module must expose a `run(netlist_str, fig, params=None)` function.
"""

import importlib
import pkgutil
from pathlib import Path

# Discover sub-modules (we will add more later)
_package_path = Path(__file__).parent
__all__ = []

for mod in pkgutil.iter_modules([str(_package_path)]):
    if mod.name.startswith("_"):
        continue
    importlib.import_module(f"{__name__}.{mod.name}")
    __all__.append(mod.name)
