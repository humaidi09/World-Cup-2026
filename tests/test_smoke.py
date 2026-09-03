"""The demo in main.py must run end to end without raising."""

import runpy


def test_main_runs_clean(capsys):
    runpy.run_module("main", run_name="__main__")
    out = capsys.readouterr().out
    assert "MATCH START" in out
    assert "France National Team" in out
    # The squad section should list all four registered players.
    assert "SQUAD" in out
    assert "Mbappe" in out and "Lloris" in out
