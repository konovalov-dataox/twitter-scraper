import typing
from setup_requirements import setup


class AcceleratorModule:
    modules = {}

    def __init__(self, name: str, requirements: typing.List[str]):
        self.name = name
        self.requirements = requirements
        self.module_class = None
        self.is_init = True

    @classmethod
    def declare_module(cls, name: str, requirements: typing.List[str]):
        if name in cls.modules:
            return cls.modules[name]
        module = cls(name, requirements)
        cls.modules[name] = module
        return module

    def init(self):
        setup(self.requirements)

    def __bool__(self):
        return not self.is_init

    def __repr__(self):
        return f'<AcceleratorModule({self.name})>'
