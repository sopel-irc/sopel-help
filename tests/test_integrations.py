"""Integration tests for the sopel-help plugin."""
import pytest
from sopel.tests import rawlist


TMP_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable = coretasks, help
"""


@pytest.fixture
def tmpconfig(configfactory):
    return configfactory('test.cfg', TMP_CONFIG)


@pytest.fixture
def mockbot(tmpconfig, botfactory):
    return botfactory.preloaded(tmpconfig, preloads=['help'])


@pytest.fixture
def irc(mockbot, ircfactory):
    return ircfactory(mockbot)


def test_help(irc, userfactory):
    user = userfactory('Exirel')
    irc.pm(user, '.help')

    assert irc.bot.backend.message_sent[0] == rawlist(
        "PRIVMSG Exirel :Here is my list of commands:",
    )[0]
    assert len(irc.bot.backend.message_sent) > 1, 'More than one line expected'


def test_help_command(irc, userfactory):
    user = userfactory('Exirel')
    irc.pm(user, '.help help')

    assert irc.bot.backend.message_sent == rawlist(
        "PRIVMSG Exirel :Generate help for Sopel's commands.",
        "PRIVMSG Exirel :e.g. .help help or .help",
    )


def test_help_command_unknown(irc, userfactory):
    user = userfactory('Exirel')
    irc.pm(user, '.help doesnotexist')

    assert irc.bot.backend.message_sent == rawlist(
        "PRIVMSG Exirel :Unknown command \"doesnotexist\"",
    )


def test_help_command_channel(irc, userfactory):
    user = userfactory('Exirel')
    irc.say(user, '#sopel', '.help help')

    assert irc.bot.backend.message_sent == rawlist(
        "PRIVMSG #sopel :Exirel: Generate help for Sopel's commands.",
        "PRIVMSG #sopel :e.g. .help help or .help",
    )
