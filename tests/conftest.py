import inspect
from importlib import import_module
from pathlib import Path
from types import FunctionType, ModuleType

import pytest

MODULE_NAME = "tests.sample.functions"


def get_module_type() -> ModuleType:
    return import_module(MODULE_NAME)


def get_members(module_type: ModuleType) -> list[tuple[str, FunctionType]]:
    return inspect.getmembers(module_type, inspect.isfunction)


def get_module_type_with_functions() -> tuple[ModuleType, list[FunctionType]]:
    module_type = get_module_type()
    return (
        module_type,
        [member[1] for member in get_members(module_type)],
    )


@pytest.fixture
def python_package_path(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    tmp_path.joinpath(MODULE_NAME + ".py").write_text("import os")
    return tmp_path


@pytest.fixture
def module_name() -> str:
    return MODULE_NAME


@pytest.fixture
def module_type() -> ModuleType:
    return get_module_type()


@pytest.fixture
def members() -> list[tuple[str, FunctionType]]:
    return get_members(get_module_type())


@pytest.fixture
def module_type_with_functions() -> tuple[ModuleType, list[FunctionType]]:
    return get_module_type_with_functions()


@pytest.fixture
def module_types_with_functions() -> list[tuple[ModuleType, list[FunctionType]]]:
    return [get_module_type_with_functions()]
