import pytest


def test_default_app():
    from repocribro.app import app
    import flask
    assert isinstance(app, flask.Flask)


def test_main_manager(capsys):
    with pytest.raises(SystemExit):
        import repocribro.__main__
    out, err = capsys.readouterr()
    assert 'usage' in out
    assert 'arguments' in out
    assert 'config ' in out
    assert 'version ' in out
    assert 'help ' in out


def test_manager(capsys):
    with pytest.raises(SystemExit):
        from repocribro.manage import run
        run()
    out, err = capsys.readouterr()
    assert 'usage' in out
    assert 'arguments' in out
    assert 'config ' in out
    assert 'version ' in out
    assert 'help ' in out
