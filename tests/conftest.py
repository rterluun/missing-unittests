import inspect
from argparse import Namespace
from importlib import import_module
from pathlib import Path
from types import FunctionType, ModuleType
from typing import LiteralString

import pytest

from missing_unittests.config import MissingUnittestsConfig, MissingUnittestsYamlConfig

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


def get_python_package_folder_structure() -> tuple[list[LiteralString], str]:
    module_name_split = MODULE_NAME.split(".")
    sub_dirs = module_name_split[:-1]
    file_name = module_name_split[-1] + ".py"
    return (sub_dirs, file_name)


@pytest.fixture
def python_package_path(tmp_path: Path) -> tuple[Path, Path, Path]:
    sub_dirs, file_name = get_python_package_folder_structure()
    sub_dir_path = tmp_path.joinpath(*sub_dirs)
    file_path = tmp_path.joinpath(*sub_dirs, file_name)
    sub_dir_path.mkdir(parents=True, exist_ok=True)
    file_path.write_text("import os")
    file_path_relative = file_path.relative_to(tmp_path)

    return (tmp_path, sub_dir_path, file_path_relative)


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


@pytest.fixture
def argparse_namespace() -> Namespace:
    return Namespace(
        src_folder="./src/",
        tests_folder="./tests/",
        fail_on_missing_tests=True,
        config_file=Path(__file__).parent / "config" / "config.yaml",
    )


def get_exclusions_list() -> list[tuple[str, str]]:
    return [
        ("missing_unittests.__init__", "a"),
        ("missing_unittests.__init__", "b"),
        ("missing_unittests.__main__", "a"),
    ]


@pytest.fixture
def config_yaml() -> Path:
    return Path(__file__).parent / "config" / "config.yaml"


@pytest.fixture
def missing_unittests_yaml_config() -> MissingUnittestsYamlConfig:
    return MissingUnittestsYamlConfig(
        exclusions=[
            {"module": "missing_unittests.__init__", "functions": ["a", "b"]},
            {"module": "missing_unittests.__main__", "functions": ["a"]},
        ]
    )


@pytest.fixture
def exclusions_list() -> list[tuple[str, str]]:
    return get_exclusions_list()


@pytest.fixture
def missing_unittests_config() -> MissingUnittestsConfig:
    exclusions_list = get_exclusions_list()
    return MissingUnittestsConfig(exclusions=exclusions_list)
