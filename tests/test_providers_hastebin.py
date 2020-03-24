import pytest

from sopel_help import providers

MOCK_KEY = 'testkey'
MOCK_URL = 'https://hastebin.com/documents'


def test_publish(requests_mock):
    requests_mock.post(MOCK_URL, json={
        'key': MOCK_KEY,
    })

    # this provider doesn't need any bot setup to work
    provider = providers.HasteBinPublisher()
    provider.setup(None)

    # this provider doesn't need any bot or trigger, just the content
    result = provider.publish(None, None, 'This is my content.')

    assert result == 'https://hastebin.com/%s' % MOCK_KEY, (
        'The HasteBinPublisher must return an URL built with the key')


def test_publish_error(requests_mock):
    requests_mock.post(MOCK_URL, status_code=404)

    # this provider doesn't need any bot setup to work
    provider = providers.HasteBinPublisher()
    provider.setup(None)

    with pytest.raises(providers.PublishingError):
        provider.publish(None, None, 'This is my content.')


def test_publish_not_json(requests_mock):
    requests_mock.post(MOCK_URL, text='not-json-data')

    # this provider doesn't need any bot setup to work
    provider = providers.HasteBinPublisher()
    provider.setup(None)

    with pytest.raises(providers.PublishingError):
        provider.publish(None, None, 'This is my content.')


def test_publish_json_missing_key(requests_mock):
    requests_mock.post(MOCK_URL, json={
        'notkey': MOCK_KEY,
    })

    # this provider doesn't need any bot setup to work
    provider = providers.HasteBinPublisher()
    provider.setup(None)

    with pytest.raises(providers.PublishingError):
        provider.publish(None, None, 'This is my content.')
