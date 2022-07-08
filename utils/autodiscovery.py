from glob import glob
from importlib import import_module, util
from inspect import getmembers
from pathlib import Path
from os.path import split
from types import ModuleType
from typing import Union
from sanic import Sanic

from sanic.blueprints import Blueprint


def autodiscover(app: Sanic, *module_names: Union[str, ModuleType], recursive: bool = False) -> None:
    """
    `autodiscover` will detect all blueprint defined in module_names and register to `app`.
    """
    mod = app.__module__
    blueprints = set()
    _imported = set()

    def _find_bps(module: object) -> None:
        nonlocal blueprints

        for _, member in getmembers(module):
            if isinstance(member, Blueprint):
                blueprints.add(member)

    for module in module_names:
        if isinstance(module, str):
            module = import_module(module, mod)
            _imported.add(module.__file__)
        _find_bps(module)

        if recursive:
            if module.__file__:
                base = Path(module.__file__).parent
                for path in glob(f"{base}/**/*.py", recursive=True):
                    if path not in _imported:
                        name = "module"
                        if "__init__" in path:
                            *_, name, __ = split(path)
                        spec = util.spec_from_file_location(name, path)
                        _imported.add(path)
                        if spec:
                            specmod = util.module_from_spec(spec)
                            if spec.loader:
                                spec.loader.exec_module(specmod)
                        _find_bps(specmod)

    for bp in blueprints:
        app.blueprint(bp)
