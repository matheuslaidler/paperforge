"""Smoke tests for the Typer CLI surface."""

from typer.testing import CliRunner

from paperforge.cli import app

runner = CliRunner()


def test_root_help_lists_subcommands() -> None:
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    out = res.stdout
    for cmd in ("pdf", "slides", "chart", "config"):
        assert cmd in out


def test_version_flag() -> None:
    from paperforge import __version__
    res = runner.invoke(app, ["--version"])
    assert res.exit_code == 0
    assert __version__ in res.stdout


def test_config_show_path() -> None:
    res = runner.invoke(app, ["config", "--path"])
    assert res.exit_code == 0
    assert "config.yaml" in res.stdout


def test_config_set_and_reset() -> None:
    res = runner.invoke(app, ["config", "--set", "lang=pt_br"])
    assert res.exit_code == 0
    res = runner.invoke(app, ["config", "--reset"])
    assert res.exit_code == 0


def test_config_set_invalid_key_fails() -> None:
    res = runner.invoke(app, ["config", "--set", "nonsense=42"])
    assert res.exit_code == 2
