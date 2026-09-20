from pathlib import Path
from unittest.mock import MagicMock, patch

from src.missing_unittests.scan import (
    get_modules_from_folder,
)


@patch("src.missing_unittests.scan.get_module_types")
def test_get_modules_from_folder(
    mock_get_module_types: MagicMock,
    tmp_path: Path,
):
    folder = tmp_path.joinpath("src")
    folder.mkdir(parents=True, exist_ok=True)
    module_name = "module1"

    folder.joinpath(module_name + ".py").write_text("import os")

    with patch(
        "src.missing_unittests.scan._convert_path_to_module_name"
    ) as mock_convert_path:
        mock_convert_path.return_value = module_name

        get_modules_from_folder(folder=folder)

        mock_get_module_types.assert_called_once_with(
            module_name=module_name, is_source_folder=False
        )
