from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import mark

from missing_unittests.__init__ import fail_on_missing_tests, main
from missing_unittests.config import MissingUnittestsConfig
from missing_unittests.scan import PrecommitHookError


@patch("missing_unittests.__init__.sys.exit")
@patch("missing_unittests.__init__.find_src_functions_not_in_tests")
@patch("missing_unittests.__init__.argparse.ArgumentParser.parse_known_args")
def test_main_calls_functions_with_correct_arguments(
    mock_parse_known_args: MagicMock,
    mock_find_src_functions_not_in_tests: MagicMock,
    mock_sys_exit: MagicMock,
    argparse_namespace: Namespace,
    missing_unittests_config: MissingUnittestsConfig,
) -> None:
    mock_parse_known_args.return_value = (argparse_namespace, [])
    main()

    mock_find_src_functions_not_in_tests.assert_called_once_with(
        src_folder=Path(argparse_namespace.src_folder),
        tests_folder=Path(argparse_namespace.tests_folder),
        config=missing_unittests_config,
    )

    mock_sys_exit.assert_called_once_with(0)


@patch("missing_unittests.__init__.sys.exit")
@patch("missing_unittests.__init__.find_src_functions_not_in_tests")
@patch("missing_unittests.__init__.argparse.ArgumentParser.parse_known_args")
def test_main_calls_sys_exit_1_when_fail_on_missing_tests_is_true_and_exception_raised(
    mock_parse_known_args: MagicMock,
    mock_find_src_functions_not_in_tests: MagicMock,
    mock_sys_exit: MagicMock,
    argparse_namespace: Namespace,
) -> None:
    mock_parse_known_args.return_value = (argparse_namespace, [])
    mock_find_src_functions_not_in_tests.side_effect = PrecommitHookError(
        "a error occurred"
    )
    main()
    mock_sys_exit.assert_called_once_with(1)


@patch("missing_unittests.__init__.sys.exit")
@patch("missing_unittests.__init__.find_src_functions_not_in_tests")
@patch("missing_unittests.__init__.argparse.ArgumentParser.parse_known_args")
def test_main_calls_sys_exit_0_when_fail_on_missing_tests_is_false_and_exception_raised(
    mock_parse_known_args: MagicMock,
    mock_find_src_functions_not_in_tests: MagicMock,
    mock_sys_exit: MagicMock,
    argparse_namespace: Namespace,
) -> None:
    argparse_namespace.fail_on_missing_tests = False
    mock_parse_known_args.return_value = (argparse_namespace, [])
    mock_find_src_functions_not_in_tests.side_effect = PrecommitHookError(
        "a error occurred"
    )
    main()
    mock_sys_exit.assert_called_once_with(0)


@mark.parametrize("env_value", ["true", "1", "t", "y", "yes"])
@patch("missing_unittests.__init__.environ")
def test_fail_on_missing_tests_when_env_var_is_set_to_true(
    mock_environ: MagicMock,
    env_value: str,
) -> None:
    mock_environ.get.return_value = env_value
    assert fail_on_missing_tests() is True
