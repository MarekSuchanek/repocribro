

def test_mock_landing(repocribro_app):
    assert repocribro_app.get('/').status == '200 OK'
    assert '<h1>repocribro</h1>' in \
           repocribro_app.get('/').data.decode('utf-8')
