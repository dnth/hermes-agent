"""run_git must spawn git windowless so the periodic Projects-tree probe
doesn't flash a console per repo on a console-less Windows backend (#53178).

Behavior contract: run_git routes through the _subprocess_compat hidden-spawn
primitive (CREATE_NO_WINDOW on Windows, no-op on POSIX) rather than spawning a
bare console git, and never spawns at all for an empty cwd.
"""

from __future__ import annotations

from types import SimpleNamespace

import tui_gateway.git_probe as gp


def test_run_git_routes_through_hidden_spawn(monkeypatch):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        return SimpleNamespace(returncode=0, stdout="main\n")

    monkeypatch.setattr("hermes_cli._subprocess_compat.run", fake_run)

    assert gp.run_git("/repo", "branch", "--show-current") == "main"
    assert seen["cmd"][:2] == ["git", "-C"]


def test_run_git_empty_cwd_does_not_spawn(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("run_git must not spawn for an empty cwd")

    monkeypatch.setattr("hermes_cli._subprocess_compat.run", boom)

    assert gp.run_git("") == ""
