from pathlib import Path
from types import FunctionType, ModuleType
from unittest.mock import MagicMock, patch

from missing_unittests.scan import (
    _convert_path_to_module_name,
    _get_modules_from_folder,
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


# @patch("missing_unittests.scan._filter_functions_from_module")
# @patch("missing_unittests.scan._get_functions_from_module_types")
# def test_get_module_types_calls_get_functions_and_filter_functions(
#     mock_get_functions_from_module_types: MagicMock,
#     mock_filter_functions_from_module: MagicMock,
#     module_name: str,
#     module_type: ModuleType,
# ):
#     _get_module_types(module_name=module_name, is_source_folder=True)
#     mock_get_functions_from_module_types.assert_called_once_with(
#         module_type=module_type
#     )

#     mock_filter_functions_from_module.assert_called_once_with(
#         module_type_with_functions=mock_get_functions_from_module_types.return_value
#     )


# @patch("missing_unittests.scan._filter_functions_from_module")
# @patch("missing_unittests.scan._get_functions_from_module_types")
# def test_get_module_types_returns(
#     mock_get_functions_from_module_types: MagicMock,
#     mock_filter_functions_from_module: MagicMock,
#     module_name: str,
#     module_type_with_functions: tuple[ModuleType, list[FunctionType]],
# ):
#     mock_get_functions_from_module_types.return_value = module_type_with_functions

#     assert (
#         _get_module_types(module_name=module_name, is_source_folder=False)
#         == module_type_with_functions
#     )

#     mock_filter_functions_from_module.assert_not_called()


# @patch("missing_unittests.scan.getmembers")
# def test_get_functions_from_module_types_calls_getmembers(
#     mock_getmembers: MagicMock,
#     module_type: ModuleType,
# ):
#     _get_functions_from_module_types(module_type=module_type)
#     mock_getmembers.assert_called_once_with(module_type, isfunction)


# @patch("missing_unittests.scan.getmembers")
# def test_get_functions_from_module_types_returns(
#     mock_getmembers: MagicMock,
#     module_type: ModuleType,
#     module_type_with_functions: tuple[ModuleType, list[FunctionType]],
#     members: list[tuple[str, FunctionType]],
# ):
#     mock_getmembers.return_value = members
#     assert (
#         _get_functions_from_module_types(module_type=module_type)
#         == module_type_with_functions
#     )


# @patch("missing_unittests.scan.getmembers")
# def test_filter_functions_from_module_returns(
#     mock_getmembers: MagicMock,
#     module_type_with_functions: tuple[ModuleType, list[FunctionType]],
#     members: list[tuple[str, FunctionType]],
#     module_name: str,
# ):
#     mock_getmembers.return_value = members

#     functions = _filter_functions_from_module(
#         module_type_with_functions=module_type_with_functions
#     )

#     assert [
#         member.__name__ for member in functions[1] if member.__module__ == module_name
#     ] == [
#         "sample_function",
#         "test_function",
#     ]


# def test_find_not_imported_functions_in_tests(
#     module_types_with_functions: list[tuple[ModuleType, list[FunctionType]]],
# ):
#     not_imported_functions_in_tests = _find_not_imported_functions_in_tests(
#         src_modules=module_types_with_functions,
#         test_modules=module_types_with_functions,
#     )

#     assert not_imported_functions_in_tests == [("_pytest.raises", "raises")]
