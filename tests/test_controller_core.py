

def test_landing(app_client):
    assert app_client.get('/').status == '200 OK'
    assert '<h1>repocribro</h1>' in \
           app_client.get('/').data.decode('utf-8')


def test_search(app_client):
    assert app_client.get('/search').status == '200 OK'
    assert '<h1>Search</h1>' in \
           app_client.get('/search').data.decode('utf-8')
    assert '<h1>Search</h1>' in \
           app_client.get('/search/yolo').data.decode('utf-8')
    assert 'yolo' in \
           app_client.get('/search/yolo').data.decode('utf-8')
