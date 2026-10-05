from pathlib import Path
from unittest.mock import MagicMock, patch

from missing_unittests.config import (
    MissingUnittestsConfig,
    MissingUnittestsYamlConfig,
    get_exclusions_from_yaml_config,
    load_config,
    load_config_from_yaml,
)


def test_load_config_from_yaml_nonexistent_file():
    assert (
        load_config_from_yaml(config_yaml=Path("nonexistent_config.yaml"))
        == MissingUnittestsYamlConfig()
    )


def test_load_config_from_yaml_nonconfig_file():
    assert (
        load_config_from_yaml(config_yaml=Path(__file__))
        == MissingUnittestsYamlConfig()
    )


def test_load_config_from_yaml_valid_config_file(
    config_yaml: Path,
    missing_unittests_yaml_config: MissingUnittestsYamlConfig,
):
    assert (
        load_config_from_yaml(config_yaml=config_yaml) == missing_unittests_yaml_config
    )


def test_get_exclusions_from_yaml_config(
    missing_unittests_yaml_config: MissingUnittestsYamlConfig,
    exclusions_list: list[tuple[str, str]],
):
    assert (
        get_exclusions_from_yaml_config(config=missing_unittests_yaml_config)
        == exclusions_list
    )


@patch("missing_unittests.config.get_exclusions_from_yaml_config")
@patch("missing_unittests.config.load_config_from_yaml")
def test_load_config(
    mock_load_config_from_yaml: MagicMock,
    mock_get_exclusions_from_yaml_config: MagicMock,
    config_yaml: Path,
    missing_unittests_yaml_config: MissingUnittestsYamlConfig,
    missing_unittests_config: MissingUnittestsConfig,
    exclusions_list: list[tuple[str, str]],
):
    mock_load_config_from_yaml.return_value = missing_unittests_yaml_config
    mock_get_exclusions_from_yaml_config.return_value = exclusions_list
    assert load_config(config_yaml=config_yaml) == missing_unittests_config

    mock_load_config_from_yaml.assert_called_once_with(config_yaml=config_yaml)
    mock_get_exclusions_from_yaml_config.assert_called_once_with(
        config=missing_unittests_yaml_config
    )
