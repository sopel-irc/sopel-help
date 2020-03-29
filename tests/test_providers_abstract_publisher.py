import time

import pytest

from sopel.tests import rawlist
from sopel_help import providers

TMP_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable = coretasks, help
"""


class MockPublisher(providers.AbstractPublisher):
    def publish(self, bot, trigger, content):
        return 'https://example.com/content'


class MockTimePublisher(providers.AbstractPublisher):
    def publish(self, bot, trigger, content):
        return 'https://example.com/%s' % time.monotonic()


@pytest.fixture
def tmpconfig(configfactory):
    return configfactory('test.cfg', TMP_CONFIG)


@pytest.fixture
def mockbot(tmpconfig, botfactory):
    return botfactory.preloaded(tmpconfig, preloads=['help'])


def test_publish():
    abstract = providers.AbstractPublisher()
    with pytest.raises(NotImplementedError):
        abstract.publish(None, None, None)


def test_render():
    abstract = providers.AbstractPublisher()

    result = abstract.render(None, None, ['line 1', 'line 2'])
    assert result == 'line 1\n\nline 2'


def test_send_help_commands(mockbot, triggerfactory):
    provider = MockPublisher()
    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG #channel :.help')

    provider.send_help_commands(
        wrapper, wrapper._trigger, ['line 1', 'line 2'])

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG #channel :Test: I've published a list of my commands at: "
        "https://example.com/content",
    )


def test_send_help_commands_private(mockbot, triggerfactory):
    provider = MockPublisher()
    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG %s :.help' % mockbot.nick)

    provider.send_help_commands(
        wrapper, wrapper._trigger, ['line 1', 'line 2'])

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG Test :I've published a list of my commands at: "
        "https://example.com/content",
    )


def test_use_cache():
    provider = providers.AbstractPublisher()

    assert provider.get_cached_value(None) is None

    provider.save_cache('sign', 'value')

    assert provider.get_cached_value('sign') == 'value'
    assert provider.get_cached_value('not sign') is None


def test_send_help_commands_cache(mockbot, triggerfactory):
    lines = ['line 1', 'line 2']
    provider = MockTimePublisher()
    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG %s :.help' % mockbot.nick)
    content = provider.render(wrapper, wrapper._trigger, lines)
    signature = provider.get_cache_signature(
        wrapper, wrapper._trigger, content)

    assert provider.get_cached_value(signature) is None

    provider.send_help_commands(wrapper, wrapper._trigger, lines)

    cached_url = provider.get_cached_value(signature)
    assert cached_url is not None

    provider.send_help_commands(wrapper, wrapper._trigger, lines)

    assert cached_url == provider.get_cached_value(signature)

    provider.send_help_commands(wrapper, wrapper._trigger, lines + ['line 3'])

    assert provider.get_cached_value(signature) is None
