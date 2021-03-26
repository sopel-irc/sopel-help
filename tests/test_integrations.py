"""Integration tests for the sopel-help plugin."""
from unittest import mock

import pytest
from sopel.tests import rawlist
from sopel.tools import get_input

from sopel_help.plugin import configure

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


def test_configure(tmpconfig):
    with mock.patch('sopel.config.types.get_input') as mock_input:
        mock_input.side_effect = ["ubuntu", "query"]
        configure(tmpconfig)

    assert 'help' in tmpconfig
    assert hasattr(tmpconfig.help, 'output')
    assert hasattr(tmpconfig.help, 'reply_method')
    assert hasattr(tmpconfig.help, 'line_threshold')

    assert tmpconfig.help.output == 'ubuntu'
    assert tmpconfig.help.reply_method == 'query'
    assert tmpconfig.help.line_threshold == 3


def test_configure_local(tmpconfig):
    with mock.patch('sopel.config.types.get_input') as mock_input:
        mock_input.side_effect = [
            "local",
            "query",
            "https://example.com/sopel/",
            "custom.html",
            "/home/sopel/help",
        ]
        configure(tmpconfig)

    assert 'help' in tmpconfig
    assert hasattr(tmpconfig.help, 'output')
    assert hasattr(tmpconfig.help, 'reply_method')
    assert hasattr(tmpconfig.help, 'origin_base_url')
    assert hasattr(tmpconfig.help, 'origin_output_name')
    assert hasattr(tmpconfig.help, 'origin_output_dir')

    assert tmpconfig.help.output == 'local'
    assert tmpconfig.help.reply_method == 'query'
    assert tmpconfig.help.origin_base_url == 'https://example.com/sopel/'
    assert tmpconfig.help.origin_output_name == 'custom.html'
    assert tmpconfig.help.origin_output_dir == '/home/sopel/help'


def test_configure_local_default(tmpconfig):
    with mock.patch('sopel.config.types.get_input') as mock_input:
        mock_input.side_effect = [
            "local",
            "query",
            "https://example.com/sopel/",
            "",
            "",
        ]
        configure(tmpconfig)

    assert tmpconfig.help.output == 'local'
    assert tmpconfig.help.reply_method == 'query'
    assert tmpconfig.help.origin_base_url == 'https://example.com/sopel/'
    assert tmpconfig.help.origin_output_name == 'help.html'
    assert tmpconfig.help.origin_output_dir == '/var/www/html'
