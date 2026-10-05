from pathlib import Path

import yaml
from pydantic import BaseModel


class MissingUnittestsYamlConfig(BaseModel):
    exclusions: list = []


class MissingUnittestsConfig(BaseModel):
    exclusions: list[tuple[str, str]] = []


def load_config_from_yaml(config_yaml: Path) -> MissingUnittestsYamlConfig:
    data: dict = {}

    try:
        if not config_yaml.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_yaml}. Using default configuration."
            )

        file_content: dict | None = None

        with open(config_yaml, "r", encoding="utf-8") as f:
            file_content = yaml.safe_load(f)

        if isinstance(file_content, dict):
            data = file_content

    except FileNotFoundError as e:
        print(e)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {config_yaml}: {e}")

    config = MissingUnittestsYamlConfig(**data)

    return config


def get_exclusions_from_yaml_config(
    config: MissingUnittestsYamlConfig,
) -> list[tuple[str, str]]:
    exclusions: list = [
        (exclusion.get("module"), function)
        for exclusion in config.exclusions
        for function in exclusion.get("functions", [])
    ]

    exclusions_str: list[tuple[str, str]] = [
        (module, function)
        for module, function in exclusions
        if isinstance(module, str) and isinstance(function, str)
    ]

    return exclusions_str


def load_config(config_yaml: Path):
    yaml_config: MissingUnittestsYamlConfig = load_config_from_yaml(
        config_yaml=config_yaml
    )

    return MissingUnittestsConfig(
        exclusions=get_exclusions_from_yaml_config(config=yaml_config),
    )
