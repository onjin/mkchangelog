import re

import pytest

from mkchangelog import main


def test_cli_generate(capsys: pytest.CaptureFixture[str]):
    main(["generate", "--stdout"])
    captured = capsys.readouterr()
    assert captured.out.startswith("# Changelog")


def test_cli_bump(capsys: pytest.CaptureFixture[str]):
    main(["bump", "-v", "6.6.6", "--dry-run"])
    captured = capsys.readouterr()
    out = re.sub(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]", "", captured.out)

    assert "v6.6.6" in out
