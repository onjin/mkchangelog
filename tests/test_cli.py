import pytest

from mkchangelog import main


@pytest.mark.skip("TODO")
def test_changelog_command(capsys: pytest.CaptureFixture[str]):
    main(["changes"])
    captured = capsys.readouterr()
    assert captured.out == "marker"
