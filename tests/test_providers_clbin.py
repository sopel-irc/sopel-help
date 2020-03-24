import pytest

from sopel_help import providers

MOCK_RESULT = 'https://example.com/clbin-content'
MOCK_URL = 'https://clbin.com/'


def test_publish(requests_mock):
    requests_mock.post(MOCK_URL, text=MOCK_RESULT)

    # this provider doesn't need any bot setup to work
    provider = providers.CLBinPublisher()
    provider.setup(None)

    # this provider doesn't need any bot or trigger, just the content
    result = provider.publish(None, None, 'This is my content.')

    assert result == MOCK_RESULT, (
        'The CLBinPublisher must return the response text as-is')


def test_publish_error(requests_mock):
    requests_mock.post(MOCK_URL, status_code=404)

    # this provider doesn't need any bot setup to work
    provider = providers.CLBinPublisher()
    provider.setup(None)

    with pytest.raises(providers.PublishingError):
        provider.publish(None, None, 'This is my content.')
