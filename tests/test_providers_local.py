import pytest
from sopel.tests import rawlist

from sopel_help import providers

TMP_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable = coretasks, help

[help]
output = local
origin_base_url = https://example.com/sopel/
origin_output_name = help.html
origin_output_dir = /tmp/
"""

CHANNEL_LINE = ':Test!test@example.com PRIVMSG #channel :.help'
QUERY_LINE = ':Test!test@example.com PRIVMSG TestBot :.help'


@pytest.fixture
def tmpconfig(configfactory):
    return configfactory('test.cfg', TMP_CONFIG)


@pytest.fixture
def mockbot(tmpconfig, botfactory):
    return botfactory.preloaded(tmpconfig, preloads=['help'])


def test_send_help_commands(mockbot, triggerfactory, tmpdir):
    mockbot.settings.help.origin_output_dir = str(tmpdir.mkdir('docs'))
    print(mockbot.settings.help.origin_output_dir)

    provider = providers.LocalFile()
    provider.setup(mockbot)
    wrapper = triggerfactory.wrapper(mockbot, CHANNEL_LINE)

    provider.send_help_commands(
        wrapper, wrapper._trigger, ['line 1', 'line 2'])

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG #channel :Test: I've published a list of my commands at: "
        "https://example.com/sopel/help.html",
    )
