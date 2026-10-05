from inspect import isfunction
from pathlib import Path
from types import FunctionType, ModuleType
from unittest.mock import MagicMock, patch

import pytest

from missing_unittests.config import MissingUnittestsConfig
from missing_unittests.scan import (
    PrecommitHookError,
    _convert_path_to_module_name,
    _filter_functions_from_module,
    _find_not_imported_functions_in_tests,
    _get_functions_from_module_types,
    _get_module_types,
    _get_modules_from_folder,
    find_src_functions_not_in_tests,
)


def test_convert_path_to_module_name_not_source_folder(
    python_package_path: tuple[Path, Path, Path],
    module_name: str,
):
    _, _, file_path = python_package_path
    assert (
        _convert_path_to_module_name(path=file_path, is_source_folder=False)
        == module_name
    )


def test_convert_path_to_module_name_source_folder():
    file_path = "src/missing_unittests/scan.py"
    assert (
        _convert_path_to_module_name(path=Path(file_path), is_source_folder=True)
        == "missing_unittests.scan"
    )


@patch("missing_unittests.scan._convert_path_to_module_name")
@patch("missing_unittests.scan._get_module_types")
def test_get_modules_from_folder_calls_helpers_with_correct_arguments(
    mock_get_module_types: MagicMock,
    mock_convert_path: MagicMock,
    python_package_path: tuple[Path, Path, Path],
    module_name: str,
):
    tmp_path, _, file_path = python_package_path
    mock_convert_path.return_value = module_name

    _get_modules_from_folder(
        folder=tmp_path.joinpath("tests"),
        is_source_folder=False,
    )

    mock_convert_path.assert_called_once_with(path=file_path, is_source_folder=False)

    mock_get_module_types.assert_called_once_with(
        module_name=module_name, is_source_folder=False
    )


@patch("missing_unittests.scan._convert_path_to_module_name")
@patch("missing_unittests.scan._get_module_types")
def test_get_modules_from_folder_returns(
    mock_get_module_types: MagicMock,
    mock_convert_path: MagicMock,
    python_package_path: tuple[Path, Path, Path],
    module_type_with_functions: tuple[ModuleType, list[FunctionType]],
):
    tmp_path, _, _ = python_package_path
    mock_get_module_types.return_value = module_type_with_functions

    returns = _get_modules_from_folder(
        folder=tmp_path.joinpath("tests"),
        is_source_folder=False,
    )

    assert returns == [module_type_with_functions]
    mock_convert_path.assert_called()


@patch("missing_unittests.scan.print")
@patch("missing_unittests.scan._convert_path_to_module_name")
def test_get_modules_from_folder_raises_value_error_when_module_not_found(
    mock_convert_path: MagicMock,
    mock_print: MagicMock,
    python_package_path: tuple[Path, Path, Path],
):
    tmp_path, _, _ = python_package_path
    module_name = "non_existent_module"
    mock_convert_path.return_value = module_name

    _get_modules_from_folder(
        folder=tmp_path.joinpath("tests"),
        is_source_folder=False,
    )

    mock_print.assert_called_with(
        f"Module '{module_name}' not found. Please check the module name."
    )


@patch("missing_unittests.scan._filter_functions_from_module")
@patch("missing_unittests.scan._get_functions_from_module_types")
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


@patch("missing_unittests.scan._filter_functions_from_module")
@patch("missing_unittests.scan._get_functions_from_module_types")
def test_get_module_types_raises_value_error_when_module_not_found(
    mock_get_functions_from_module_types: MagicMock,
    mock_filter_functions_from_module: MagicMock,
):
    module_name = "non_existent_module"
    with pytest.raises(
        ValueError,
        match=f"Module '{module_name}' not found. Please check the module name.",
    ):
        _get_module_types(module_name=module_name, is_source_folder=True)
        mock_get_functions_from_module_types.assert_called()
        mock_filter_functions_from_module.assert_not_called()


@patch("missing_unittests.scan._filter_functions_from_module")
@patch("missing_unittests.scan._get_functions_from_module_types")
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


@patch("missing_unittests.scan.getmembers")
def test_get_functions_from_module_types_calls_getmembers(
    mock_getmembers: MagicMock,
    module_type: ModuleType,
):
    _get_functions_from_module_types(module_type=module_type)
    mock_getmembers.assert_called_once_with(module_type, isfunction)


@patch("missing_unittests.scan.getmembers")
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


@patch("missing_unittests.scan.getmembers")
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


def test_find_not_imported_functions_in_tests(
    module_types_with_functions: list[tuple[ModuleType, list[FunctionType]]],
    exclusions_list: list[tuple[str, str]],
):
    with pytest.raises(
        PrecommitHookError,
        match=r"Pre-commit hook failed: Missing unit tests for functions:",
    ):
        _find_not_imported_functions_in_tests(
            src_modules=module_types_with_functions,
            test_modules=module_types_with_functions,
            exclusions=exclusions_list,
        )


@patch("missing_unittests.scan._find_not_imported_functions_in_tests")
@patch("missing_unittests.scan._get_modules_from_folder")
def test_find_src_functions_not_in_tests(
    mock_get_modules_from_folder: MagicMock,
    mock_find_not_imported_functions_in_tests: MagicMock,
    missing_unittests_config: MissingUnittestsConfig,
):
    src_folder = Path("src")
    tests_folder = Path("tests")

    find_src_functions_not_in_tests(
        src_folder=src_folder,
        tests_folder=tests_folder,
        config=missing_unittests_config,
    )

    assert mock_get_modules_from_folder.call_count == 2
    mock_get_modules_from_folder.assert_any_call(
        folder=src_folder,
        is_source_folder=True,
    )
    mock_get_modules_from_folder.assert_any_call(
        folder=tests_folder,
    )

    mock_find_not_imported_functions_in_tests.assert_called_once_with(
        src_modules=mock_get_modules_from_folder.return_value,
        test_modules=mock_get_modules_from_folder.return_value,
        exclusions=missing_unittests_config.exclusions,
    )


@patch("missing_unittests.scan._find_not_imported_functions_in_tests")
@patch("missing_unittests.scan._get_modules_from_folder")
def test_find_src_functions_raises_precommit_hook_error_when_missing_unittests(
    mock_get_modules_from_folder: MagicMock,
    mock_find_not_imported_functions_in_tests: MagicMock,
    missing_unittests_config: MissingUnittestsConfig,
):
    src_folder = Path("src")
    tests_folder = Path("tests")

    mock_find_not_imported_functions_in_tests.side_effect = PrecommitHookError(
        "some error"
    )

    with pytest.raises(
        PrecommitHookError, match="Pre-commit hook failed due to missing unit tests."
    ):
        find_src_functions_not_in_tests(
            src_folder=src_folder,
            tests_folder=tests_folder,
            config=missing_unittests_config,
        )
        mock_get_modules_from_folder.assert_called()
