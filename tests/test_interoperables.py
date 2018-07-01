import pytest


def test_default_app():
    from repocribro.app import app
    import flask
    assert isinstance(app, flask.Flask)


def test_main_manager(capsys):
    with pytest.raises(SystemExit):
        import repocribro.__main__
    out, err = capsys.readouterr()
    print(out)
    assert 'Usage' in out
    assert 'Options' in out
    assert 'Commands' in out
    assert 'run ' in out
    assert 'version ' in out
    assert 'help ' in out


def test_manager(capsys):
    with pytest.raises(SystemExit):
        from repocribro.cli import cli
        cli()
    out, err = capsys.readouterr()
    assert 'Usage' in out
    assert 'Options' in out
    assert 'Commands' in out
    assert 'run ' in out
    assert 'version ' in out
    assert 'help ' in out
