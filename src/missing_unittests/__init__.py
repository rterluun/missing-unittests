import argparse
from pathlib import Path
from sys import exit, path

from missing_unittests.scan import (
    MissingUnittestsError,
    find_src_functions_not_in_tests,
)


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

    args, _ = parser.parse_known_args()
    path.append(".")

    try:
        find_src_functions_not_in_tests(
            src_folder=Path(args.src_folder),
            tests_folder=Path(args.tests_folder),
        )
    except MissingUnittestsError as e:
        print(f"Error: {e}")
        exit(1)
