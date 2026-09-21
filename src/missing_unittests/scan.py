from importlib import import_module
from inspect import getmembers, isfunction
from os import walk
from pathlib import Path
from types import FunctionType, ModuleType


def find_not_imported_functions_in_tests(
    src_modules: list[tuple[ModuleType, list[FunctionType]]],
    test_modules: list[tuple[ModuleType, list[FunctionType]]],
) -> list[tuple[str, str]]:
    not_imported_functions_in_tests = []

    for src_module in src_modules:
        try:
            src_module_type = src_module[0]
            found_test_functions = []

            for test_module in test_modules:
                found_test_functions.extend(
                    [
                        tst_function.__name__
                        for tst_function in test_module[1]
                        if tst_function.__module__ == src_module_type.__name__
                    ]
                )

            not_imported_functions_in_tests.extend(
                [
                    (src_function.__module__, src_function.__name__)
                    for src_function in src_module[1]
                    if src_function.__name__ not in found_test_functions
                ]
            )
        except TypeError:
            continue

    return not_imported_functions_in_tests


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
) -> list[tuple[ModuleType, list[FunctionType]]]:
    modules: list[tuple[ModuleType, list[FunctionType]]] = []

    for root, _, files in walk(str(folder)):
        is_source_folder: bool = False

        if str(Path(root)).startswith("src"):
            is_source_folder = True

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


def show_missing_unittests(coverage: list[tuple[str, str, bool]]):
    coverage_perc = (
        len([function for function in coverage if function[2]]) / len(coverage) * 100
    )

    print(f"Coverage: {coverage_perc:.2f}%")
    for module_name, function_name, is_tested in coverage:
        print(f"Module: {module_name}, Function: {function_name} - Tested: {is_tested}")


def calculate_coverage(
    src_modules: list[tuple[ModuleType, list[FunctionType]]],
    not_imported_functions_in_tests: list[tuple[str, str]],
) -> list[tuple[str, str, bool]]:
    total_functions = []
    _ = [
        total_functions.extend(src_module[1])
        for src_module in src_modules
        if isinstance(src_module[1], list)
    ]

    not_imported_functions = [
        (str(function[0]), str(function[1]), False)
        for function in [
            (function.__module__, function.__name__) for function in total_functions
        ]
        if function in not_imported_functions_in_tests
    ]

    imported_functions = [
        (str(function[0]), str(function[1]), True)
        for function in [
            (function.__module__, function.__name__) for function in total_functions
        ]
        if function not in not_imported_functions_in_tests
    ]

    return not_imported_functions + imported_functions


def find_src_functions_not_in_tests(
    src_folder: Path,
    tests_folder: Path,
) -> None:
    src_modules: list[tuple[ModuleType, list[FunctionType]]] = _get_modules_from_folder(
        folder=src_folder
    )
    test_modules: list[tuple[ModuleType, list[FunctionType]]] = (
        _get_modules_from_folder(folder=tests_folder)
    )

    not_imported_functions_in_tests = find_not_imported_functions_in_tests(
        src_modules=src_modules, test_modules=test_modules
    )

    coverage = calculate_coverage(
        src_modules=src_modules,
        not_imported_functions_in_tests=not_imported_functions_in_tests,
    )

    show_missing_unittests(coverage=coverage)
