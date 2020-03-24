import pytest

from sopel_help import providers

MOCK_RESULT = '/p/example'
MOCK_URL = 'https://pastebin.ubuntu.com/'


def test_publish(requests_mock):
    requests_mock.post(MOCK_URL, status_code=302, headers={
        'location': MOCK_RESULT,
    })

    # this provider doesn't need any bot setup to work
    provider = providers.UbuntuPublisher()
    provider.setup(None)

    # this provider doesn't need any bot or trigger, just the content
    result = provider.publish(None, None, 'This is my content.')

    assert result == 'https://pastebin.ubuntu.com/p/example', (
        'The UbuntuPublisher must return the response location header')


def test_publish_error(requests_mock):
    requests_mock.post(MOCK_URL, status_code=404)

    # this provider doesn't need any bot setup to work
    provider = providers.UbuntuPublisher()
    provider.setup(None)

    with pytest.raises(providers.PublishingError):
        provider.publish(None, None, 'This is my content.')
