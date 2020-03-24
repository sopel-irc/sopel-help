import socket
from unittest import mock

import pytest

from sopel_help import providers

MOCK_RESULT = 'https://example.com/clbin-content'


def test_publish():
    # this provider doesn't need any bot setup to work
    provider = providers.TermBinPublisher()
    provider.setup(None)

    with mock.patch('socket.socket') as mock_socket:
        mock_socket.return_value.recv.side_effect = [MOCK_RESULT, ""]

        # this provider doesn't need any bot or trigger, just the content
        result = provider.publish(None, None, 'This is my content.')

    assert result == MOCK_RESULT, (
        'The CLBinPublisher must return the response text as-is')


def test_publish_error():
    # this provider doesn't need any bot setup to work
    provider = providers.TermBinPublisher()
    provider.setup(None)

    with mock.patch('socket.socket') as mock_socket:
        mock_socket.return_value.recv.side_effect = socket.error()

        with pytest.raises(providers.PublishingError):
            provider.publish(None, None, 'This is my content.')
