import pytest

from mkchangelog import main


def test_cli_changes(capsys: pytest.CaptureFixture[str]):
    main(["changes"])
    captured = capsys.readouterr()
    assert captured.out.startswith("## HEAD")


def test_cli_generate(capsys: pytest.CaptureFixture[str]):
    main(["generate"])
    captured = capsys.readouterr()
    assert captured.out.startswith("# Changelog")


def test_cli_bump(capsys: pytest.CaptureFixture[str]):
    main(["bump", "-s", "6.6.6", "--dry-run"])
    captured = capsys.readouterr()
    assert "v6.6.6" in captured.out
