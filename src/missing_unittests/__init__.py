import argparse
import sys
from os import environ
from pathlib import Path
from sys import path

from missing_unittests.scan import (
    PrecommitHookError,
    find_src_functions_not_in_tests,
)


def fail_on_missing_tests() -> bool:
    fail_on_missing_tests_env = environ.get("FAIL_ON_MISSING_TESTS", "False")
    return fail_on_missing_tests_env.lower() in ("true", "1", "t", "y", "yes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src-folder",
        type=str,
        default="./src/",
        help="Path to the source folder",
    )
    parser.add_argument(
        "--tests-folder",
        type=str,
        default="./tests/",
        help="Path to the tests folder",
    )
    parser.add_argument(
        "--fail-on-missing-tests",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Fail the pre-commit hook if missing tests are found",
    )

    args, _ = parser.parse_known_args()
    path.append(".")
    exitcode = 0

    try:
        find_src_functions_not_in_tests(
            src_folder=Path(args.src_folder),
            tests_folder=Path(args.tests_folder),
        )
    except PrecommitHookError:
        if args.fail_on_missing_tests is True or fail_on_missing_tests():
            exitcode = 1

    sys.exit(exitcode)
