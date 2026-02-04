# python/registry.py

class Registry:
    _modules = {}

    @classmethod
    def register(cls, name: str, module):
        cls._modules[name] = module

    @classmethod
    def get(cls, name: str):
        if name not in cls._modules:
            raise KeyError(f"Module {name} not found in registry")
        return cls._modules[name]

    @classmethod
    def all_modules(cls):
        return cls._modules.keys()
