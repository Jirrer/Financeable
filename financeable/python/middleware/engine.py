# python/middleware/engine.py
from .loader import Loader
from .registry import Registry
from .router import Router

class Engine:
    def __init__(self):
        print("ENGINE CONSTRUCTOR")

    def load(self, name: str, path: str):
        module = Loader.load_module(name, path)
        Registry.register(name, module)
        print("MODELS LOADED")

    def call(self, module_name: str, method_name: str, *args, **kwargs):
        return Router.call(module_name, method_name, *args, **kwargs)
