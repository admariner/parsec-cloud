#!/usr/bin/env python3
# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

"""
This script is used to ease the parsec release process.

The produced tag is going to be signed so make sure you have a GPG key available.
If not, it can be generated using the following command:

    $ gpg --gen-key

A typical release process looks as follow:

    # Switch to master and make sure all the latest commits are pulled
    $ git checkout master
    $ git pull master

    # Run the releaser script with the expected version
    $ ./misc/releaser.py build v1.2.3

    # Push the produced tag and commits
    $ git push --follow-tags

    # Alternatively, you can revert the commits and delete the tag in case you made
    # an error (of course don't do that if you have already push the changes !)
    $ ./misc/releaser.py rollback

"""

from __future__ import annotations

import argparse
import enum
import math
import os
import re
import subprocess
import sys
import textwrap
from collections import defaultdict
from collections.abc import Callable
from copy import copy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import version_updater  # type: ignore (pyright struggles with this when run from server folder)

PYTHON_EXECUTABLE_PATH = sys.executable
LICENSE_CONVERSION_DELAY = 4 * 365 * 24 * 3600  # 4 years
PROJECT_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_DIR / "HISTORY.rst"
BUSL_LICENSE_FILE = PROJECT_DIR / "LICENSE"

FRAGMENTS_DIR = PROJECT_DIR / "newsfragments"
FRAGMENT_TYPES = {
    "feature": "Features",
    "bugfix": "Bugfixes",
    "doc": "Improved Documentation",
    "removal": "Deprecations and Removals",
    "api": "Client/Server API evolutions",
    "misc": "Miscellaneous internal changes",
    "empty": "Miscellaneous internal changes that shouldn't even be collected",
}
COLOR_END = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_DIM = "\033[2m"
DESCRIPTION = f"""TL,DR:
Create release commit&tag: {COLOR_GREEN}./misc/releaser.py build v1.2.3{COLOR_END}
Oops I've made a mistake: {COLOR_GREEN}./misc/releaser.py rollback{COLOR_END}
    """ + (
    __doc__ if __doc__ else ""
)  # __doc__ is "str | None", see https://github.com/microsoft/pyright/discussions/3820

PRERELEASE_EXPR = r"(?P<pre_l>(a|b|rc))\.?(?P<pre_n>[0-9]+)"

# Inspired by https://peps.python.org/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
RELEASE_REGEX = re.compile(
    r"^"
    r"v?"
    r"(?P<release>(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+))"
    rf"(?:-(?P<pre>{PRERELEASE_EXPR}))?"
    r"(?:.dev\.(?P<dev>[0-9]+))?"
    r"(?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?"
    r"$"
)

DRY_GIT_COMMANDS = os.environ.get("DRY_GIT", "0") == "1"


class ReleaseError(Exception):
    pass


class Version:
    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: str | None = None,
        dev: int | None = None,
        local: str | None = None,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre: None | tuple[str, int] = None
        self._dev = dev
        self.local: str | None = local

        if prerelease is not None:
            self.prerelease = prerelease

    @classmethod
    def parse(cls, raw: str, git: bool = False) -> Version:
        raw = raw.strip()
        raw = raw.removeprefix("v")
        if git:
            # Git describe show our position relative to an existing release.
            # `git describe` could return for example `1.2.3-15-g3b5f5762`, here:
            #
            # - `1.2.3` is the `major.minor.patch`.
            # - `-15` indicate that we have `15` commit since the tag `1.2.3`.
            # - `-g3b5f5762` indicate that we are currently on the commit `3b5f5762`.
            #
            # A semver compatible version could be `1.2.3-dev.15+git.3b5f5762`
            #
            # Convert `1.2.3-N-gSHA` to `1.2.3-dev.N+git.SHA`
            raw, _ = re.subn(
                pattern=r"-(\d+)-g([0-9A-Za-z]+)",
                repl=r"-dev.\1+git.\2",
                string=raw,
                count=1,
            )
        match = RELEASE_REGEX.match(raw)
        if not match:
            raise ValueError(
                f"Invalid version format {raw!r}, should be `[v]<major>.<minor>.<patch>[-<post>][+dev|-<X>-g<commit>]` (e.g. `v1.0.0`, `1.2.3+dev`, `1.6.7-rc1`)"
            )

        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))
        prerelease = match.group("pre")
        dev = int(match.group("dev")) if match.group("dev") is not None else None
        local = match.group("local")

        return Version(major, minor, patch, prerelease=prerelease, dev=dev, local=local)

    def evolve(self, **kwargs: Any) -> Version:
        new = copy(self)
        for k, v in kwargs.items():
            setattr(new, k, v)
        return new

    def to_pep440(self) -> str:
        """
        Format the version into `pep440` format, will have the same format as the version present in wheel filename.

        I don't use `pip._vender.packaging.utils.canonicalize_version` because it strip the trailing `.0`,
        in the version number and the generated wheel have the trailing `0` included :(.
        """

        parts: list[str] = []

        parts.append(f"{self.major}.{self.minor}.{self.patch}")

        if self.pre is not None:
            part, id = self.pre
            parts.append(f"{part}{id}")

        if self.dev is not None:
            parts.append(f".dev{self.dev}")

        if self.local is not None:
            parts.append(f"+{self.local}")

        return "".join(parts)

    def without_local(self) -> Version:
        return self.evolve(local=None)

    def docker_tag(self) -> str:
        """
        Format the version into a docker tag.
        A docker tag is human-readable identifier composed of [a-zA-Z0-9_.-]
        https://docs.docker.com/reference/cli/docker/image/tag/
        """
        return str(self).replace("+", ".")

    def __repr__(self) -> str:
        return f"Version(major={self.major}, minor={self.minor}, patch={self.patch}, prerelease={self.prerelease}, dev={self.dev}, local={self.local})"

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        prerelease = self.prerelease
        sep = "-"
        if prerelease is not None:
            base += sep + prerelease
            sep = "."
        if self.dev is not None:
            base += f"{sep}dev.{self.dev}"
        if self.local is not None:
            base += "+" + self.local
        return base

    @property
    def is_preversion(self) -> bool:
        return self.pre is not None

    @property
    def prerelease(self) -> str | None:
        if self.pre is not None:
            return f"{self.pre[0]}.{self.pre[1]}"
        else:
            return None

    @prerelease.setter
    def prerelease(self, raw: str) -> None:
        match = re.match(PRERELEASE_EXPR, raw)
        assert match is not None
        self.pre = (match.group("pre_l"), int(match.group("pre_n")))

    @property
    def dev(self) -> int | None:
        return self._dev

    @dev.setter
    def dev(self, raw: int) -> None:
        self._dev = raw

    @property
    def is_dev(self) -> bool:
        return self.dev is not None

    def type(self) -> str:
        if self.is_dev:
            return "dev"
        elif self.is_alpha:
            return "alpha"
        elif self.is_beta:
            return "beta"
        elif self.is_rc:
            return "release-candidate"
        else:
            return "production"

    @property
    def is_alpha(self) -> bool:
        return self.prerelease is not None and self.prerelease.startswith("a.")

    @property
    def is_beta(self) -> bool:
        return self.prerelease is not None and self.prerelease.startswith("b.")

    @property
    def is_rc(self) -> bool:
        return self.prerelease is not None and self.prerelease.startswith("rc.")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            string_other = str(other)
        elif isinstance(other, tuple):
            string_other = (
                "v"
                + ".".join([str(i) for i in other[:3]])
                + (f"-{''.join(other[3:])}" if len(other) > 3 else "")
            )
        else:
            raise TypeError(f"Unsupported type `{type(other).__name__}`")

        return str(self) == string_other

    def __lt__(self, other: Version) -> bool:
        k = (self.major, self.minor, self.patch)
        other_k = (other.major, other.minor, other.patch)

        def _pre_type_to_val(pre_type: str) -> int:
            return {"a": 1, "b": 2, "rc": 3}[pre_type]

        if k == other_k:
            # Must take into account dev and pre info
            if self.pre is not None:
                type, index = self.pre
                pre_type: int | float = _pre_type_to_val(type)
                pre_index: int | float = index
            else:
                pre_type = pre_index = math.inf

            if other.pre is not None:
                type, index = other.pre
                other_pre_type: int | float = _pre_type_to_val(type)
                other_pre_index: int | float = index
            else:
                other_pre_type = other_pre_index = math.inf

            dev = self.dev or 0
            other_dev = other.dev or 0

            local = self.local is not None
            other_local = other.local is not None

            return (pre_type, pre_index, dev, local) < (
                other_pre_type,
                other_pre_index,
                other_dev,
                other_local,
            )

        else:
            return k < other_k

    def __le__(self, other: Version) -> bool:
        if self == other:
            return True
        else:
            return self < other


# Version is non-trivial code, so let's run some pseudo unit tests...
def _test_parse_version_string(raw: str, expected: Version, git: bool = False) -> None:
    v = Version.parse(raw, git)
    assert v == expected, f"From raw version `{raw}`, we parsed `{v}` but we expected `{expected}`"


def _test_format_version(version: Version, expected: str) -> None:
    s = str(version)
    assert s == expected, (
        f"Version {version!r} is not well formatted: got `{s}` but expected `{expected}`"
    )


_test_parse_version_string("1.2.3", Version(1, 2, 3))
_test_parse_version_string("1.2.3+dev", Version(1, 2, 3, local="dev"))
_test_parse_version_string(
    "1.2.3-10-g3b5f5762", Version(1, 2, 3, dev=10, local="git.3b5f5762"), git=True
)
_test_parse_version_string(
    "v2.12.1-2160-g1c38d13f8",
    Version(2, 12, 1, dev=2160, local="git.1c38d13f8"),
    git=True,
)
_test_parse_version_string("1.2.3-b42", Version(1, 2, 3, prerelease="b42"))
_test_parse_version_string("1.2.3-rc1+dev", Version(1, 2, 3, prerelease="rc1", local="dev"))
_test_parse_version_string("v2.15.0+dev.2950f88", Version(2, 15, 0, local="dev.2950f88"))
_test_parse_version_string(
    "2.16.0-a.0.dev.19786+a4f9627ee",
    Version(2, 16, 0, prerelease="a.0", dev=19786, local="a4f9627ee"),
)
assert Version.parse("1.2.3") < Version.parse("1.2.4")
assert Version.parse("1.2.3-a1") < Version.parse("1.2.3-a2")
assert Version.parse("1.2.3-a10") < Version.parse("1.2.3-b1")
assert Version.parse("1.2.3-b10") < Version.parse("1.2.3-rc1")
assert Version.parse("1.2.3-b1") < Version.parse("1.2.3-b1+dev")
assert Version.parse("1.2.3-rc1") < Version.parse("1.2.3")
assert Version.parse("1.2.3") < Version.parse("1.2.3+dev")
assert Version.parse("1.2.3+dev") < Version.parse("1.2.4-rc1")
assert Version.parse("1.2.4-rc1") < Version.parse("1.2.4-rc1+dev")
assert Version.parse("1.2.4-rc1+dev") < Version.parse("1.2.4")
assert Version.parse("1.2.3") < Version.parse("1.2.3-10-g3b5f5762", git=True)
assert Version.parse("1.2.3-10-g3b5f5762", git=True) < Version.parse("1.2.4-b42")
assert Version.parse("1.2.4-b42") < Version.parse("1.2.4-b42-10-g3b5f5762", git=True)
assert Version.parse("1.2.4-b42-10-g3b5f5762", git=True) < Version.parse("1.2.4")
assert Version.parse("1.2.3-rc10+dev") < Version.parse("1.2.3")
assert Version.parse("1.2.3-b10+dev") < Version.parse("1.2.3-rc1+dev")
assert Version.parse("1.2.3-b10+dev") < Version.parse("1.2.3+dev")
assert Version(1, 2, 3, local="foo").without_local() == Version(1, 2, 3)
_test_format_version(Version(1, 2, 3), "1.2.3")
_test_format_version(Version(1, 2, 3, prerelease="a1"), "1.2.3-a.1")
_test_format_version(Version(1, 2, 3, prerelease="b2", dev=4), "1.2.3-b.2.dev.4")
_test_format_version(Version(1, 2, 3, dev=0), "1.2.3-dev.0")
_test_format_version(Version(1, 2, 3, dev=5), "1.2.3-dev.5")
_test_format_version(Version(1, 2, 3, prerelease="a1", local="foo.bar"), "1.2.3-a.1+foo.bar")
_test_format_version(
    Version(1, 2, 3, prerelease="b2", dev=4, local="foo.bar"), "1.2.3-b.2.dev.4+foo.bar"
)
_test_format_version(Version(1, 2, 3, dev=4, local="foo.bar"), "1.2.3-dev.4+foo.bar")


def run_git(*cmd: Any, verbose: bool = False) -> str:
    if DRY_GIT_COMMANDS:
        print(
            f"{COLOR_DIM}[DRY] >> git {' '.join(map(str, cmd))}{COLOR_END}",
            file=sys.stderr,
        )
        return ""
    return run_cmd("git", *cmd, verbose=verbose)


def run_cmd(*cmd: Any, verbose: bool = False) -> str:
    print(f"{COLOR_DIM}>> {' '.join(map(str, cmd))}{COLOR_END}", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Error while running `{cmd}`: returned {proc.returncode}\n"
            f"stdout:\n{proc.stdout.decode()}\n"
            f"stderr:\n{proc.stderr.decode()}\n"
        )
    stderr = proc.stderr.decode()
    if verbose and stderr:
        print(
            f"[Stderr stream from {COLOR_RED}{cmd}{COLOR_END}]\n{stderr}[End stderr stream]",
            file=sys.stderr,
        )
    return proc.stdout.decode()


def get_version_from_code() -> Version:
    return Version.parse(version_updater.get_tool_version(version_updater.Tool.Parsec))


def update_version_files(version: Version) -> set[Path]:
    """
    Update the required files to the provided version.
    Return the set of updated files
    """
    version_updater.set_tool_version(version_updater.Tool.Parsec, str(version))
    res = version_updater.check_tool(version_updater.Tool.Parsec, update=True)
    if res.errors:
        raise ReleaseError("Error while updating version files:\n" + "\n".join(res.errors))
    return res.updated


def update_license_file(
    version: Version, new_release_date: datetime, same_version: bool
) -> set[Path]:
    license_txt = BUSL_LICENSE_FILE.read_text(encoding="utf8")
    half_updated_license_txt = re.sub(
        r"Change Date:.*",
        f"Change Date:  {new_release_date.strftime('%b %d, %Y')}",
        license_txt,
    )
    if not same_version:
        updated_version_txt = re.sub(
            r"Licensed Work:.*",
            f"Licensed Work:  Parsec v{version}",
            half_updated_license_txt,
        )
        assert updated_version_txt != half_updated_license_txt, (
            f"The `Licensed Work` field should have changed, but hasn't (likely because the new version `{version}` correspond to the version written on the license file)"
        )
    else:
        updated_version_txt = half_updated_license_txt
    BUSL_LICENSE_FILE.write_bytes(
        updated_version_txt.encode("utf8")
    )  # Use write_bytes to keep \n on Windows
    return {BUSL_LICENSE_FILE}


def collect_newsfragments() -> list[Path]:
    fragments: list[Path] = []
    fragment_regex = re.compile(r"^[0-9]+\.(" + "|".join(FRAGMENT_TYPES.keys()) + r")\.rst$")
    for entry in FRAGMENTS_DIR.iterdir():
        if entry.name in (".gitkeep", "README.rst"):
            continue
        # Sanity check
        if not fragment_regex.match(entry.name) or not entry.is_file():
            raise ReleaseError(f"Invalid entry detected in newsfragments dir: `{entry.name}`")
        fragments.append(entry)

    return fragments


def get_release_branch(version: Version) -> str:
    return f"releases/{version.major}.{version.minor}"


def ensure_working_in_a_clean_git_repo() -> None:
    stdout = run_git("status", "--porcelain", "--untracked-files=no")
    if stdout.strip():
        raise ReleaseError("Repository is not clean, aborting")


def ensure_working_on_the_correct_branch(
    release_branch: str, base_ref: str | None, version: Version, nightly: bool
) -> None:
    current_branch = run_git("rev-parse", "--abbrev-ref", "HEAD").strip()
    print(f"Current branch {COLOR_GREEN}{current_branch}{COLOR_END}")

    if current_branch == release_branch:
        print("Already in the release branch, nothing to do")
        return

    # Force use of the release branch for the next patch version or nightly build
    if version.patch == 0 or nightly:
        print("Creating release branch...")
        run_git(
            "switch",
            "--force-create",
            release_branch,
            *([base_ref] if base_ref else []),
        )
    else:
        raise ReleaseError(
            f"""
        It seems you are trying to create a patched release from the wrong base branch.
        Use base branch `{release_branch}` if you want to create a patched release.
        (commits related to the patch release should be pushed to that branch before)
        """
        )


def get_licence_eol_date(release_date: datetime) -> datetime:
    # Cannot just add years to date given it wouldn't handle february 29th
    license_eol_date = datetime.fromtimestamp(release_date.timestamp() + LICENSE_CONVERSION_DELAY)
    assert release_date.toordinal() < license_eol_date.toordinal()
    return license_eol_date


def update_history_changelog(
    newsfragments: list[Path], version: Version, yes: bool, release_date: datetime
) -> set[Path]:
    history_header, history_body = split_history_file()

    issues_per_type: defaultdict[str, list[str]] = convert_newsfragments_to_rst(newsfragments)

    new_entry = gen_rst_release_entry(version, release_date, issues_per_type)

    updated_history_txt = f"{history_header}{new_entry}{history_body}".strip() + "\n"
    HISTORY_FILE.write_bytes(
        updated_history_txt.encode("utf8")
    )  # Use write_bytes to keep \n on Windows

    print("New entry in `history.rst`:\n\n```")
    print(new_entry)
    print("```")

    # Make git commit

    if not yes:
        input(
            f"Pausing so you can check {COLOR_YELLOW}HISTORY.rst{COLOR_END} is okay, press any key when ready"
        )

    return {HISTORY_FILE}


def create_bump_commit_to_new_version(
    new_version: Version,
    current_version: Version,
    newsfragments: list[Path],
    files_to_commit: set[Path],
    gpg_sign: bool,
) -> None:
    commit_msg = f"Bump version {current_version} -> {new_version}"
    print(f"Create commit {COLOR_GREEN}{commit_msg}{COLOR_END}")
    run_git("add", *files_to_commit)
    if newsfragments:
        fragments_paths = [str(x.absolute()) for x in newsfragments]
        run_git("rm", *fragments_paths)
    # FIXME: the `releaser` steps in pre-commit is disable is `no-verify` still required ?
    # Disable pre-commit hooks given this commit wouldn't pass `releaser check`
    run_git(
        "commit",
        f"--message={commit_msg}",
        "--no-verify",
        "--gpg-sign" if gpg_sign else "--no-gpg-sign",
    )


def create_tag_for_new_version(
    version: Version, tag: str, gpg_sign: bool, force_mode: GitForceMode
) -> None:
    print(f"Create tag {COLOR_GREEN}{tag}{COLOR_END}")
    run_git(
        "tag",
        *(force_mode.tag_args),
        tag,
        f"--message=Release version {version}",
        "--annotate",
        "--sign" if gpg_sign else "--no-sign",
    )


def inspect_tag(tag: str, yes: bool, gpg_sign: bool) -> None:
    print(f"Inspect tag {COLOR_GREEN}{tag}{COLOR_END}")

    if gpg_sign:
        print(run_git("show", tag, "--show-signature", "--quiet"))
        print(run_git("tag", "--verify", tag))

    if not yes:
        input("Check if the generated git tag is okay... (press any key to continue)")


def create_bump_commit_to_dev_version(
    version: Version, license_eol_date: datetime, gpg_sign: bool, same_version: bool
) -> None:
    dev_version = generate_next_dev_version(version)

    updated_files: set[Path] = set()
    updated_files |= update_license_file(dev_version, license_eol_date, same_version)
    updated_files |= update_version_files(dev_version)

    create_bump_commit_to_new_version(
        new_version=dev_version,
        current_version=version,
        newsfragments=[],
        files_to_commit=updated_files,
        gpg_sign=gpg_sign,
    )


def generate_next_dev_version(version: Version) -> Version:
    """
    Generate the next development version based on the provided version.

    If the version is a pre-release, the next version will be the same with the pre-release number increased.
    Otherwise, its patch will be increased and the pre-release will be set to `a0`.

    In all cases the local part will be set to `dev`.
    """
    next = version.evolve(local="dev")
    if next.pre is None:
        next.patch += 1
        next.pre = ("a", 0)
    else:
        next.pre = (next.pre[0], next.pre[1] + 1)
    return next


assert generate_next_dev_version(Version(1, 2, 3)) == Version(1, 2, 4, prerelease="a0", local="dev")
assert generate_next_dev_version(Version(1, 0, 0)) == Version(1, 0, 1, prerelease="a0", local="dev")
# Should only increase the pre-release number if set in the version
assert generate_next_dev_version(Version(1, 2, 3, prerelease="a0")) == Version(
    1, 2, 3, prerelease="a1", local="dev"
)


def push_release(
    tag: str, release_branch: str, yes: bool, force_mode: GitForceMode, skip_tag: bool
) -> None:
    print("Pushing changes to remote...")

    if not yes:
        input("Press any key to push the changes to the remote server")
    # Push the release branch and the tag at the same time
    print(
        run_git(
            "push",
            "--set-upstream",
            "--atomic",
            *(force_mode.push_args),
            "origin",
            release_branch,
            *([] if skip_tag else [tag]),
        )
    )


def gen_rst_release_entry(
    version: Version,
    release_date: datetime,
    issues_per_type: defaultdict[str, list[str]],
) -> str:
    new_entry_title = f"Parsec v{version} ({release_date.date().isoformat()})"
    new_entry = f"\n\n{new_entry_title}\n{len(new_entry_title) * '-'}\n"

    if not issues_per_type:
        new_entry += "\nNo significant changes.\n"
    else:
        for fragment_type, fragment_title in FRAGMENT_TYPES.items():
            if fragment_type not in issues_per_type:
                continue
            new_entry += f"\n{fragment_title}\n{len(fragment_title) * '~'}\n\n"
            new_entry += "\n".join(issues_per_type[fragment_type])
            new_entry += "\n"
    return new_entry


def convert_newsfragments_to_rst(
    newsfragments: list[Path],
) -> defaultdict[str, list[str]]:
    issues_per_type: defaultdict[str, list[str]] = defaultdict(list)
    for fragment in newsfragments:
        issue_id, type, _ = fragment.name.split(".")
        # Don't add empty fragments. Still needed to be collected as they will be deleted later
        if type == "empty":
            continue
        issue_txt = f"{fragment.read_text(encoding='utf8')}"
        wrapped_issue_txt = textwrap.fill(
            issue_txt,
            width=80,
            break_long_words=False,
            initial_indent="* ",
            subsequent_indent="  ",
        )
        issues_per_type[type].append(
            wrapped_issue_txt
            + f"\n  (`#{issue_id} <https://github.com/Scille/parsec-cloud/issues/{issue_id}>`__)\n"
        )
    return issues_per_type


def split_history_file() -> tuple[str, str]:
    history_txt = HISTORY_FILE.read_text(encoding="utf8")
    header_split = ".. towncrier release notes start\n"
    if header_split in history_txt:
        header, history_body = history_txt.split(header_split, 1)
        history_header = header + header_split
    else:
        raise ValueError(f"Cannot the header split tag in `{HISTORY_FILE!s}`")
    return history_header, history_body


def check_release(version: Version) -> None:
    print(f"Checking release {COLOR_GREEN}{version}{COLOR_END}")

    def success() -> None:
        print(f" [{COLOR_GREEN}OK{COLOR_END}]")

    def failed() -> None:
        print(f" [{COLOR_RED}FAILED{COLOR_END}]")

    # Check __version__
    print(
        f"Validating version {COLOR_GREEN}{version}{COLOR_END} across our repo ...",
        end="",
    )
    code_version = get_version_from_code()
    if code_version != version:
        raise ReleaseError(
            f"Invalid __version__ in server/parsec/_version.py: expected `{COLOR_YELLOW}{version}{COLOR_END}`, got `{COLOR_YELLOW}{code_version}{COLOR_END}`"
        )
    version_updater.set_tool_version(version_updater.Tool.Parsec, str(version))
    version_updater.check_tool(version_updater.Tool.Parsec, update=False)
    success()

    # Check newsfragments
    print("Checking we dont have any left over fragment ...", end="")
    fragments = collect_newsfragments()
    if fragments:
        fragments_names = [fragment.name for fragment in fragments]
        failed()
        raise ReleaseError(
            f"newsfragments still contains fragments files ({', '.join(fragments_names)})"
        )
    success()

    # Check tag exist and is an annotated&signed one
    show_info = run_git("show", "--quiet", "v" + str(version))
    tag_type = show_info.split(" ", 1)[0]

    print(
        f"Checking we have an annotated tag for {COLOR_GREEN}{version}{COLOR_END} ...",
        end="",
    )
    if tag_type != "tag":
        failed()
        raise ReleaseError(f"{version} is not an annotated tag (type: {tag_type})")
    success()

    print("Checking we have signed our release commit ...", end="")
    if "BEGIN PGP SIGNATURE" not in show_info:
        failed()
        raise ReleaseError(f"{version} is not signed")
    success()


def build_main(args: argparse.Namespace) -> None:
    yes: bool = args.yes
    base_ref: str | None = args.base_ref
    current_version = get_version_from_code()
    skip_tag = args.skip_tag
    same_version = False
    git_force_mode: GitForceMode = args.git_force

    if args.nightly:
        release_version = generate_uniq_version(current_version)
        release_branch = "releases/nightly"
        git_force_mode = GitForceMode.Force
        tag = "nightly"
    else:
        if args.current:
            release_version = current_version.evolve(local=None)
            same_version = True
        elif not args.version:
            raise SystemExit(
                "Either `--version VERSION` or `--current` is required for build command"
            )
        else:
            release_version = args.version

            if current_version.evolve(local=None) == release_version:
                same_version = True

            elif release_version <= current_version:
                raise ReleaseError(
                    f"Current version is greater or equal that the new version ({COLOR_YELLOW}{current_version}{COLOR_END} >= {COLOR_YELLOW}{release_version}{COLOR_END}).\n"
                    "If you want to create a new release using the current version, use the `--current` flag instead of `--version <VERSION>`."
                )

        if release_version.is_dev:
            raise ReleaseError(
                f"Releasing a development version is not supported: {release_version}"
            )

        release_branch = get_release_branch(release_version)
        tag = "v" + str(release_version)

    print(f"Release version to build: {COLOR_GREEN}{release_version}{COLOR_END}")
    print(f"Release branch: {COLOR_GREEN}{release_branch}{COLOR_END}")
    print(f"Release commit tag: {COLOR_GREEN}{tag}{COLOR_END}")

    ensure_working_in_a_clean_git_repo()

    if not DRY_GIT_COMMANDS:
        ensure_working_on_the_correct_branch(
            release_branch, base_ref, release_version, args.nightly
        )

    release_date = datetime.now(tz=UTC)
    license_eol_date = get_licence_eol_date(release_date)

    updated_files: set[Path] = set()
    updated_files |= update_license_file(release_version, license_eol_date, same_version)
    updated_files |= update_version_files(release_version)
    newsfragments = collect_newsfragments()
    updated_files |= update_history_changelog(newsfragments, release_version, yes, release_date)

    create_bump_commit_to_new_version(
        new_version=release_version,
        current_version=current_version,
        newsfragments=newsfragments,
        files_to_commit=updated_files,
        gpg_sign=args.gpg_sign,
    )

    if not skip_tag:
        create_tag_for_new_version(
            release_version, tag, gpg_sign=args.gpg_sign, force_mode=git_force_mode
        )

        inspect_tag(tag, yes, gpg_sign=args.gpg_sign)

    # No need to create a dev version for a nightly release.
    if not args.nightly:
        create_bump_commit_to_dev_version(
            release_version,
            license_eol_date,
            gpg_sign=args.gpg_sign,
            same_version=same_version,
        )

    push_release(
        tag,
        release_branch,
        yes,
        force_mode=git_force_mode,
        skip_tag=skip_tag,
    )


def check_main(args: argparse.Namespace) -> None:
    version: Version = args.version or get_version_from_code()

    if version.is_dev:
        # TODO: rethink the non-release checks
        # check_non_release(version)
        print(f"Detected dev version {COLOR_GREEN}{version}{COLOR_END}, nothing to check...")
        pass

    else:
        check_release(version)


def rollback_main(args: argparse.Namespace) -> None:
    """
    Revert the change made by `build_release`.

    Note: for rollback to work, we expect that you don't have made and commit after `Bump version vX.Y.B -> vX.Y.B+dev` (the last commit created by `build_release`).
    """
    if run_git("diff-index", "HEAD", "--").strip():
        raise ReleaseError("Local changes are present, aborting...")

    current_version = get_version_from_code()
    if not current_version.is_dev:
        raise ReleaseError(
            f"Invalid __version__ in server/parsec/_version.py: expected {COLOR_YELLOW}vX.Y.Z+dev{COLOR_END}, got {COLOR_YELLOW}{current_version}{COLOR_END}"
        )

    version = current_version.evolve(local=None)
    print(
        f"__version__ in server/parsec/_version.py contains version {COLOR_GREEN}{current_version}{COLOR_END}, hence we should rollback version {COLOR_GREEN}{version}{COLOR_END}"
    )

    # Retrieve `Bump version vX.Y.A+dev -> vX.Y.B` and `Bump version vX.Y.B -> vX.Y.B+dev` commits
    head, head_minus_1, head_minus_2 = run_git("rev-list", "-n", "3", "HEAD").strip().splitlines()
    del head  # Unused

    tag_commit = run_git("rev-list", "-n", "1", "v" + str(version)).strip()
    if tag_commit != head_minus_1:
        raise ReleaseError(
            f"Cannot rollback as tag {COLOR_YELLOW}{version}{COLOR_END} doesn't point on {COLOR_YELLOW}HEAD^{COLOR_END}"
        )

    print(f"Removing tag {COLOR_GREEN}{version}{COLOR_END}")
    run_git("tag", "--delete", "v" + str(version))
    print(f"Reset master to {COLOR_GREEN}{head_minus_2}{COLOR_END} (i.e. HEAD~2)")
    run_git("reset", "--hard", head_minus_2)


def version_main(args: argparse.Namespace) -> None:
    raw_version: str = args.version or version_updater.get_tool_version(version_updater.Tool.Parsec)

    assert isinstance(raw_version, str)
    version = Version.parse(raw_version)
    for part in ("prerelease", "dev", "local"):
        overwritten_part = getattr(args, part, None)
        if overwritten_part is not None:
            setattr(version, part, overwritten_part)

    if args.uniq_dev:
        version = generate_uniq_version(version)

    SNAPCRAFT_MAX_VERSION_LEN = 32
    if len(str(version)) > SNAPCRAFT_MAX_VERSION_LEN:
        print(
            f"[{COLOR_YELLOW}WARNING{COLOR_END}] the version is tool long for snapcraft (current length {len(str(version))} must be <= {SNAPCRAFT_MAX_VERSION_LEN})",
            file=sys.stderr,
        )

    print(
        "\n".join(
            [
                f"full={version}",
                f"pep440={version.to_pep440()}",
                f"major={version.major}",
                f"minor={version.minor}",
                f"patch={version.patch}",
                f"prerelease={version.prerelease or ''}",
                f"dev={version.dev or ''}",
                f"local={version.local or ''}",
                f"no_local={version.without_local()}",
                f"docker={version.docker_tag()}",
                f"type={version.type()}",
            ]
        )
    )


def generate_uniq_version(version: Version) -> Version:
    SECONDS_IN_A_DAY = 24 * 3600
    now = datetime.now(tz=UTC)
    short_commit = run_git("rev-parse", "--short", "HEAD").strip()
    days_since_epoch = math.floor(now.timestamp() / SECONDS_IN_A_DAY)
    return version.evolve(dev=days_since_epoch, local=short_commit)


def acknowledge_main(args: argparse.Namespace) -> None:
    if not args.version:
        raise SystemExit("version is required for acknowledge command")

    version: Version = args.version

    if any((version.is_preversion, version.is_dev, version.local)):
        print(
            f"[{COLOR_YELLOW}WARNING{COLOR_END}] You are trying to acknowledge a non-stable version (it has a prerelease, dev or local part in the version), you are on your own"
        )

    ensure_working_in_a_clean_git_repo()

    release_branch = args.base or get_release_branch(version)
    acknowledge_branch: str = f"acknowledges/{version}"

    print(
        f"Will create a Pull-Request to acknowledge the release {COLOR_GREEN}{version}{COLOR_END}"
    )
    print(
        f"{COLOR_DIM}Will use {release_branch} as base ref when creating the branch {acknowledge_branch}{COLOR_END}"
    )

    print(run_git("switch", "--create", acknowledge_branch, release_branch))
    print(run_git("push", "--set-upstream", "origin", acknowledge_branch))

    run_cmd(
        "gh",
        "pr",
        "create",
        "--draft",
        "--base=master",
        f"--head={acknowledge_branch}",
        "--assignee=@me",
        f"--title=Acknowledge release {version}",
        "--fill",
        verbose=True,
    )


def history_main(args: argparse.Namespace) -> None:
    version: Version = get_version_from_code()
    release_date: datetime = datetime.now(tz=UTC)
    newsfragments = collect_newsfragments()
    newsfragment_rst: defaultdict[str, list[str]] = convert_newsfragments_to_rst(newsfragments)

    print(gen_rst_release_entry(version, release_date, newsfragment_rst))


class GitForceMode(enum.Enum):
    Force = "force"
    NoForce = "none"
    WithLease = "with-lease"

    @classmethod
    def values(cls) -> list[GitForceMode]:
        return list(e for e in cls)

    def __str__(self) -> str:
        return self.value

    @property
    def tag_args(self) -> list[str]:
        match self:
            case GitForceMode.NoForce:
                return []
            case GitForceMode.WithLease | GitForceMode.Force:
                return ["--force"]

    @property
    def push_args(self) -> list[str]:
        match self:
            case GitForceMode.NoForce:
                return []
            case GitForceMode.WithLease:
                return ["--force-with-lease"]
            case GitForceMode.Force:
                return ["--force"]


def cli(description: str) -> argparse.Namespace:
    def new_parser(
        name: str,
        fn: Callable[[argparse.Namespace], None],
        help: str,
        subparser: argparse._SubParsersAction[argparse.ArgumentParser],
        **parser_kwargs: Any,
    ) -> argparse.ArgumentParser:
        parser = subparser.add_parser(
            name=name,
            description=fn.__doc__,
            help=help,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            **parser_kwargs,
        )
        # We use `set_defaults` to set the function to call when the command is selected.
        parser.set_defaults(func=fn)
        return parser

    parser = argparse.ArgumentParser(
        description=description,
        # We use `RawDescriptionHelpFormatter` to not have `argparse` mess-up our formatted description.
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    subparsers = parser.add_subparsers(
        title="commands",
        required=True,
        dest="command",
    )

    build = new_parser("build", build_main, "Prepare for a new release", subparsers)
    build_exclusion = build.add_mutually_exclusive_group()
    build_exclusion.add_argument("--version", type=Version.parse, help="The new release version")
    build_exclusion.add_argument(
        "--nightly", action="store_true", help="Prepare for a new nightly release"
    )
    build_exclusion.add_argument(
        "--current",
        help=(
            "Use the current version (i.e. if `libparsec/version` contains `3.3.1-a.0+dev`,"
            " this is equivalent of doing `--version=3.3.1-a.0`)"
        ),
        action="store_true",
    )
    build.add_argument("-y", "--yes", help="Reply `yes` to asked question", action="store_true")
    build.add_argument(
        "--no-gpg-sign",
        dest="gpg_sign",
        action="store_false",
        help="Do not sign the commit or tag",
    )
    build.add_argument(
        "--git-force",
        default=GitForceMode.NoForce.value,
        const=GitForceMode.Force.value,
        type=GitForceMode,
        choices=GitForceMode.values(),
        nargs="?",
        help="Force push the release branch & tag",
    )
    build.add_argument(
        "--base",
        dest="base_ref",
        type=str,
        default=None,
        help="The base ref to use when creating the release branch",
    )
    build.add_argument(
        "--skip-tag",
        action="store_true",
        help="Skip the tag creation",
    )

    check = new_parser(
        "check",
        check_main,
        "Check that Parsec version is consistent across the repository",
        subparsers,
    )
    check.add_argument(
        "version",
        type=Version.parse,
        nargs="?",
        help="The version to use (default to `git describe`)",
    )

    new_parser("rollback", rollback_main, "Rollback the last release", subparsers)

    version = new_parser("version", version_main, "Parse a Parsec version", subparsers)
    version_exclusive_group = version.add_mutually_exclusive_group()

    version_exclusive_group.add_argument(
        "--uniq-dev", help="Generate a uniq dev version", action="store_true"
    )

    version_exclusive_group.add_argument(
        "version",
        nargs="?",
        help="Use a provided version (or the codebase version if not provided)",
        type=str,
    )

    for part in ("prerelease", "local", "dev"):
        version.add_argument(f"--{part}", help=f"Overwrite the {part} part present in the version")

    acknowledge = new_parser(
        "acknowledge",
        acknowledge_main,
        "Acknowledge a released version",
        subparsers,
        aliases=["ack"],
    )
    acknowledge.add_argument("version", type=Version.parse, help="The version to acknowledge")
    acknowledge.add_argument(
        "--base",
        type=str,
        default=None,
        help="The base ref to use when creating the acknowledge branch",
    )
    acknowledge = new_parser(
        "history",
        history_main,
        "Display history for current version",
        subparsers,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = cli(DESCRIPTION)

    args.func(args)
