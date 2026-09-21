import argparse
from pathlib import Path

from missing_unittests.scan import find_src_functions_not_in_tests  # type: ignore


def main():
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

    find_src_functions_not_in_tests(
        src_folder=Path(parser.parse_args().src_folder),
        tests_folder=Path(parser.parse_args().tests_folder),
    )


if __name__ == "__main__":
    main()
