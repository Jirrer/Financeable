# python/loader.py
import importlib.util
import sys
from types import ModuleType
from pathlib import Path

class Loader:
    @staticmethod
    def load_module(name: str, path: str) -> ModuleType:
        """Load a Python module from a file path."""
        path = Path(path)
        spec = importlib.util.spec_from_file_location(name, str(path))
        if spec is None:
            raise ImportError(f"Cannot load module {name} from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
