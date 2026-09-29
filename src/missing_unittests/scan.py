from importlib import import_module
from inspect import getmembers, isfunction
from os import walk
from pathlib import Path
from types import FunctionType, ModuleType


class MissingUnittestsError(Exception):
    """Custom exception for missing unittests."""

    def __init__(self, message: str):
        super().__init__(message)


class PrecommitHookError(Exception):
    """Custom exception for pre-commit hook errors."""

    def __init__(self, message: str):
        super().__init__(message)


def _find_not_imported_functions_in_tests(
    src_modules: list[tuple[ModuleType, list[FunctionType]]],
    test_modules: list[tuple[ModuleType, list[FunctionType]]],
) -> None:
    for src_module in src_modules:
        src_module_type = src_module[0]
        found_test_functions = []

        try:
            for test_module in test_modules:
                found_test_functions.extend(
                    [
                        tst_function.__name__
                        for tst_function in test_module[1]
                        if tst_function.__module__ == src_module_type.__name__
                    ]
                )

            missing_functions = [
                (src_function.__module__, src_function.__name__)
                for src_function in src_module[1]
                if src_function.__name__ not in found_test_functions
            ]

            if missing_functions:
                raise MissingUnittestsError(
                    f"The following functions are missing unit tests: {missing_functions}"
                )
        except MissingUnittestsError as exc:
            print(exc)
            raise PrecommitHookError(f"Pre-commit hook failed: {exc}") from exc


def _filter_functions_from_module(
    module_type_with_functions: tuple[ModuleType, list[FunctionType]],
) -> tuple[ModuleType, list[FunctionType]]:
    module_type: ModuleType = module_type_with_functions[0]
    module_functions: list[FunctionType] = [
        member[1]
        for member in getmembers(module_type, isfunction)
        if member[1].__module__ == module_type.__name__
    ]

    return (module_type, module_functions)


def _get_functions_from_module_types(
    module_type: ModuleType,
) -> tuple[ModuleType, list[FunctionType]]:
    module_functions: tuple[ModuleType, list[FunctionType]] = (
        module_type,
        [member[1] for member in getmembers(module_type, isfunction)],
    )

    return module_functions


def _get_module_types(
    module_name: str,
    is_source_folder: bool,
) -> tuple[ModuleType, list[FunctionType]]:
    module_type_with_functions: tuple[ModuleType, list[FunctionType]] = (
        ModuleType(name=""),
        [],
    )

    try:
        module_type = import_module(module_name)
        if isinstance(module_type, ModuleType):
            module_type_with_functions = _get_functions_from_module_types(
                module_type=module_type
            )
    except ModuleNotFoundError as exc:
        raise ValueError(
            f"Module '{module_name}' not found. Please check the module name."
        ) from exc

    if is_source_folder and module_type_with_functions:
        module_type_with_functions = _filter_functions_from_module(
            module_type_with_functions=module_type_with_functions
        )

    return module_type_with_functions


def _convert_path_to_module_name(path: Path) -> str:
    module_name = str(path).replace("/", ".").rstrip(".py").lstrip("src.")
    return module_name


def _get_modules_from_folder(
    folder: Path,
    is_source_folder: bool = False,
) -> list[tuple[ModuleType, list[FunctionType]]]:
    modules: list[tuple[ModuleType, list[FunctionType]]] = []

    for root, _, files in walk(str(folder)):
        module_files = [
            file for file in files if file.endswith(".py") and file != "__init__.py"
        ]

        module_names = [
            _convert_path_to_module_name(path=Path(root) / file)
            for file in module_files
        ]

        module_types = []

        try:
            module_types = [
                _get_module_types(
                    module_name=module_name,
                    is_source_folder=is_source_folder,
                )
                for module_name in module_names
            ]
        except ValueError as exc:
            print(exc)
            continue

        modules.extend(module_types)

    modules = [module for module in modules if isinstance(module, tuple)]

    return modules


def find_src_functions_not_in_tests(
    src_folder: Path,
    tests_folder: Path,
) -> None:
    src_modules: list[tuple[ModuleType, list[FunctionType]]] = _get_modules_from_folder(
        folder=src_folder,
        is_source_folder=True,
    )
    test_modules: list[tuple[ModuleType, list[FunctionType]]] = (
        _get_modules_from_folder(folder=tests_folder)
    )

    try:
        _find_not_imported_functions_in_tests(
            src_modules=src_modules, test_modules=test_modules
        )
    except PrecommitHookError as exc:
        raise PrecommitHookError(
            "Pre-commit hook failed due to missing unit tests."
        ) from exc
