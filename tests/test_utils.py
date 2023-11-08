import pytest

from mkchangelog.utils import create_version


@pytest.mark.parametrize(
    "prefix,version,result",
    [
        ("v", "v1.0.0", "1.0.0"),
        ("v", "v1.2.3", "1.2.3"),
        ("v", "v1.2", "1.2.0"),
        ("v", "v1", "1.0.0"),
    ],
)
def test_create_version(prefix: str, version: str, result: str):
    assert str(create_version(prefix, version)) == result
