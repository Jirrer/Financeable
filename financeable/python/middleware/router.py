# python/router.py
from .registry import Registry

class Router:
    @staticmethod
    def call(module_name: str, method_name: str, *args, **kwargs):
        module = Registry.get(module_name)
        method = getattr(module, method_name, None)
        if method is None:
            raise AttributeError(f"Module {module_name} has no method {method_name}")
        return method(*args, **kwargs)
