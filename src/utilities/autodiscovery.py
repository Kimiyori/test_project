from glob import glob
from importlib import import_module, util
from inspect import getmembers
from pathlib import Path
from types import ModuleType
from typing import Sequence
from sanic.blueprints import Blueprint
from sanic import Sanic


def autodiscover(
    app: Sanic, *module_names: Sequence[str], recursive: bool = False
) -> None:
    mod = app.__module__
    blueprints = set()
    _imported = set()

    def _find_bps(module: ModuleType) -> None:
        nonlocal blueprints

        for _, member in getmembers(module):
            if isinstance(member, Blueprint):
                blueprints.add(member)

    for module in module_names:
        if isinstance(module, str):
            module = import_module(module, mod)  # type: ignore
            _imported.add(module.__file__)  # type: ignore
        _find_bps(module)  # type: ignore

        if recursive:
            base = Path(module.__file__).parent  # type: ignore
            for path in glob(f"{base}/**/*.py", recursive=True):
                if path not in _imported:
                    name = "module"
                    if "__init__" in path:
                        *_, name, __ = path.split("/")
                    spec = util.spec_from_file_location(name, path)
                    specmod = util.module_from_spec(spec)  # type: ignore
                    _imported.add(path)
                    spec.loader.exec_module(specmod)  # type: ignore
                    _find_bps(specmod)
    for blueprint in blueprints:
        app.blueprint(blueprint)
