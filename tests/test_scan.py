from inspect import isfunction
from pathlib import Path
from types import FunctionType, ModuleType
from unittest.mock import MagicMock, patch

from src.missing_unittests.scan import (
    _filter_functions_from_module,
    _get_functions_from_module_types,
    _get_module_types,
    _get_modules_from_folder,
)


@patch("src.missing_unittests.scan._convert_path_to_module_name")
@patch("src.missing_unittests.scan._get_module_types")
def test_get_modules_from_folder_calls_get_module_types_with_params(
    mock_get_module_types: MagicMock,
    mock_convert_path: MagicMock,
    python_package_path: Path,
    module_name: str,
):
    mock_convert_path.return_value = module_name
    _get_modules_from_folder(folder=python_package_path)

    mock_get_module_types.assert_called_once_with(
        module_name=module_name, is_source_folder=False
    )


@patch("src.missing_unittests.scan._get_module_types")
def test_get_modules_from_folder_returns(
    mock_get_module_types: MagicMock,
    python_package_path: Path,
    module_type_with_functions: tuple[ModuleType, list[FunctionType]],
):
    mock_get_module_types.return_value = module_type_with_functions

    assert _get_modules_from_folder(folder=python_package_path) == [
        module_type_with_functions
    ]


@patch("src.missing_unittests.scan._filter_functions_from_module")
@patch("src.missing_unittests.scan._get_functions_from_module_types")
def test_get_module_types_calls_get_functions_and_filter_functions(
    mock_get_functions_from_module_types: MagicMock,
    mock_filter_functions_from_module: MagicMock,
    module_name: str,
    module_type: ModuleType,
):
    _get_module_types(module_name=module_name, is_source_folder=True)
    mock_get_functions_from_module_types.assert_called_once_with(
        module_type=module_type
    )

    mock_filter_functions_from_module.assert_called_once_with(
        module_type_with_functions=mock_get_functions_from_module_types.return_value
    )


@patch("src.missing_unittests.scan._filter_functions_from_module")
@patch("src.missing_unittests.scan._get_functions_from_module_types")
def test_get_module_types_returns(
    mock_get_functions_from_module_types: MagicMock,
    mock_filter_functions_from_module: MagicMock,
    module_name: str,
    module_type_with_functions: tuple[ModuleType, list[FunctionType]],
):
    mock_get_functions_from_module_types.return_value = module_type_with_functions

    assert (
        _get_module_types(module_name=module_name, is_source_folder=False)
        == module_type_with_functions
    )

    mock_filter_functions_from_module.assert_not_called()


@patch("src.missing_unittests.scan.getmembers")
def test_get_functions_from_module_types_calls_getmembers(
    mock_getmembers: MagicMock,
    module_type: ModuleType,
):
    _get_functions_from_module_types(module_type=module_type)
    mock_getmembers.assert_called_once_with(module_type, isfunction)


@patch("src.missing_unittests.scan.getmembers")
def test_get_functions_from_module_types_returns(
    mock_getmembers: MagicMock,
    module_type: ModuleType,
    module_type_with_functions: tuple[ModuleType, list[FunctionType]],
    members: list[tuple[str, FunctionType]],
):
    mock_getmembers.return_value = members
    assert (
        _get_functions_from_module_types(module_type=module_type)
        == module_type_with_functions
    )


@patch("src.missing_unittests.scan.getmembers")
def test_filter_functions_from_module_returns(
    mock_getmembers: MagicMock,
    module_type_with_functions: tuple[ModuleType, list[FunctionType]],
    members: list[tuple[str, FunctionType]],
    module_name: str,
):
    mock_getmembers.return_value = members

    functions = _filter_functions_from_module(
        module_type_with_functions=module_type_with_functions
    )

    assert [
        member.__name__ for member in functions[1] if member.__module__ == module_name
    ] == [
        "sample_function",
        "test_function",
    ]
