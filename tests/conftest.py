from pathlib import Path

import pytest

MODULE_NAME = "module1"


@pytest.fixture
def python_package_path(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    tmp_path.joinpath(MODULE_NAME + ".py").write_text("import os")
    return tmp_path


@pytest.fixture
def module_name() -> str:
    return MODULE_NAME
