import textwrap

from mkchangelog import BC_REGEXP, CC_REGEXP, REF_REGEXP, LogLine, get_next_version, get_references_from_msg


def test_commit_subject_regexp():
    # Given -  feature with scope
    summary = "feat(admin): super feature landed"

    # When - matched against summary regexp
    result = CC_REGEXP.match(summary)

    # Then - commit is parsed properly
    assert result.groups()[0] == None, result.groups()  # revert status
    assert result.groups()[1] == "feat", result.groups()  # type
    assert result.groups()[2] == "(admin)", result.groups()  # scope
    assert result.groups()[3] == "super feature landed", result.groups()  # title

    # And - named groups also works
    assert result.groupdict()["revert"] == None, result.groupdict()  # revert status
    assert result.groupdict()["type"] == "feat", result.groupdict()  # type
    assert result.groupdict()["scope"] == "(admin)", result.groupdict()  # scope
    assert result.groupdict()["title"] == "super feature landed", result.groupdict()  # title


def test_body_and_footer_references_regexp():
    # Given - msg with body and footer
    msg = b"""feat(admin): asdfasdfsdf

    body someid

    Closes ISS-123, ISS-432
    Relates ISS-223, ISS-232
    """
    # When - matched against full commit regexp
    result = REF_REGEXP.findall(msg.decode("utf-8"))

    # Then - we got all footer references
    assert result is not None, REF_REGEXP.pattern
    assert len(result) == 2
    assert result[0][0] == "Closes"
    assert result[0][1] == "ISS-123, ISS-432", result[0]
    assert result[1][0] == "Relates"
    assert result[1][1] == "ISS-223, ISS-232", result[1]


def test_only_footer_references_regexp():
    # Given - msg with no body and footer
    msg = b"""feat(admin): asdfasdfsdf

    Closes ISS-123, ISS-432
    Relates ISS-223, ISS-232
    """
    # When - matched against full commit regexp
    result = REF_REGEXP.findall(msg.decode("utf-8"))

    # Then - we got all footer references
    assert result is not None, REF_REGEXP.pattern
    assert len(result) == 2
    assert result[0][0] == "Closes"
    assert result[0][1] == "ISS-123, ISS-432", result[0]
    assert result[1][0] == "Relates"
    assert result[1][1] == "ISS-223, ISS-232", result[1]


def test_get_references_from_msg():
    # Given - msg with references
    msg = b"""feat(admin): asdfasdfsdf

    Closes ISS-123, ISS-432
    Relates ISS-223, ISS-232
    Closes ISS-333
    Relates ISS-444
    """

    # When - we get parsed references
    refs = get_references_from_msg(msg)

    # Then - we get dict with actions as keys and refs as values list
    assert sorted(refs["Closes"]) == ["ISS-123", "ISS-333", "ISS-432"], refs
    assert sorted(refs["Relates"]) == ["ISS-223", "ISS-232", "ISS-444"], refs


def test_gather_breaking_changes():
    # Given - breaking changes in footer
    msg = textwrap.dedent(
        """
    feat(admin): asdfasdfsdf

    some body

    BREAKING CHANGE:
        someone
        broken
        here

    Closes ISS-123, ISS-432
    Relates ISS-223, ISS-232
    """
    )
    # When - matched against regexp
    result = BC_REGEXP.findall(msg)

    # Then - we got all rows
    assert result is not None
    assert [bc.strip() for bc in result[0].split("\n") if bc] == ["someone", "broken", "here"]


def test_next_version_for_breaking_changes():
    # Given - current version and commits with breaking changes
    current_version = "v1.2.3"
    commits = [
        LogLine(
            subject="feat(api): some",
            message="feat(api): some\n\nBREAKING CHANGES: API broken\nbadly\n\n",
            revert=False,
            commit_type="feat",
            scope="(api)",
            title="some",
            references=[],
            breaking_change=["API broken"],
        )
    ]

    # When - we get next version
    version = get_next_version("v", current_version, commits)

    # Then - major segment is bumped
    assert version.name == "v2.0.0", version
