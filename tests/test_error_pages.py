import pytest


# Messages as at https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
@pytest.mark.parametrize(
    ['code', 'message'], [
        (403, 'Forbidden'),
        (404, 'Not Found'),
        (410, 'Gone'),
        (500, 'Internal Server Error'),
        (501, 'Not Implemented'),
    ]
)
def test_error_page(app_client, code, message):
    response = app_client.get('/test/error/{}'.format(code))
    assert response.status == '{} {}'.format(code, message.upper())
    assert '</html>' in response.data.decode('utf-8')
    assert message in response.data.decode('utf-8')
