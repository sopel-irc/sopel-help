import pytest
from sopel.tests import rawlist

from sopel_help import providers


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


def test_generate_help_commands():
    provider = providers.Base()

    result = list(provider.generate_help_commands({
        'group_name': ['command_a', 'command_b'],
    }))

    assert result == [
        'GROUP_NAME  command_a  command_b',
    ]


def test_generate_help_commands_many_groups():
    provider = providers.Base()

    result = list(provider.generate_help_commands({
        'group_a': ['command_a_a', 'command_a_b'],
        'group_c': ['command_c_a', 'command_c_b'],
        'group_b': ['command_b_a', 'command_b_b'],
    }))

    assert result == [
        'GROUP_A  command_a_a  command_a_b',
        'GROUP_B  command_b_a  command_b_b',
        'GROUP_C  command_c_a  command_c_b',
    ]


def test_generate_help_commands_many_lines():
    provider = providers.Base()

    result = list(provider.generate_help_commands({
        'group_a': ['command_a_a', 'command_a_b'],
        'group_c': ['command_c_a', 'command_c_b'],
        'group_b': [
            'command_b_a', 'command_b_b', 'command_b_c', 'command_b_d',
            'command_b_e', 'command_b_f', 'command_b_g', 'command_b_h',
        ],
    }))

    assert result == [
        'GROUP_A  command_a_a  command_a_b',
        'GROUP_B  command_b_a  command_b_b  command_b_c  command_b_d\n'
        '         command_b_e  command_b_f  command_b_g  command_b_h',
        'GROUP_C  command_c_a  command_c_b',
    ]


def test_generate_help_command_empty():
    provider = providers.Base()
    result = provider.generate_help_command('dostuff', [], [])

    assert len(result) == 3, '3-value tuple expected as a result'
    head, body, usages = result

    assert head == 'Command "dostuff" has no help.'
    assert body == []
    assert usages == []


def test_generate_help_command_head_only():
    provider = providers.Base()
    head, body, usages = provider.generate_help_command('dostuff', [
        'dostuff: do something very usefull for the user'
    ], [])

    assert head == 'dostuff: do something very usefull for the user'
    assert body == []
    assert usages == []


def test_generate_help_command_no_usages():
    provider = providers.Base()
    head, body, usages = provider.generate_help_command('dostuff', [
        'dostuff: do something very usefull for the user',
        'Use dostuff command when you need it most.'
    ], [])

    assert head == 'dostuff: do something very usefull for the user'
    assert body == [
        'Use dostuff command when you need it most.',
    ]
    assert usages == []


def test_generate_help_command_one_example():
    provider = providers.Base()
    head, body, usages = provider.generate_help_command('dostuff', [
        'dostuff: do something very usefull for the user',
        'Use dostuff command when you need it most.'
    ], [
        '.dostuff',
    ])

    assert head == 'dostuff: do something very usefull for the user'
    assert body == [
        'Use dostuff command when you need it most.',
    ]
    assert usages == [
        'e.g. .dostuff',
    ]


def test_generate_help_command_two_example():
    provider = providers.Base()
    head, body, usages = provider.generate_help_command('dostuff', [
        'dostuff: do something very usefull for the user',
        'Use dostuff command when you need it most.'
    ], [
        '.dostuff',
        '.dostuff foo',
    ])

    assert head == 'dostuff: do something very usefull for the user'
    assert body == [
        'Use dostuff command when you need it most.',
    ]
    assert usages == [
        'e.g. .dostuff or .dostuff foo',
    ]


def test_generate_help_command():
    provider = providers.Base()
    head, body, usages = provider.generate_help_command('dostuff', [
        'dostuff: do something very usefull for the user',
        'Use dostuff command when you need it most.'
    ], [
        '.dostuff',
        '.dostuff foo',
        '.dostuff foo bar',
    ])

    assert head == 'dostuff: do something very usefull for the user'
    assert body == [
        'Use dostuff command when you need it most.',
    ]
    assert usages == [
        'e.g. .dostuff, .dostuff foo or .dostuff foo bar',
    ]


def test_send_help_commands(mockbot, triggerfactory):
    provider = providers.Base()
    provider.setup(mockbot)

    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG #channel :.help')

    test_lines = [
        'GROUP_A  command_a_a  command_a_b',
        'GROUP_B  command_b_a  command_b_b  command_b_c  command_b_d\n'
        '         command_b_e  command_b_f  command_b_g  command_b_h',
        'GROUP_C  command_c_a  command_c_b',
    ]
    provider.send_help_commands(wrapper, wrapper._trigger, test_lines)

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG #channel :Test: I'll send you a list of commands in private.",
        "PRIVMSG Test :GROUP_A  command_a_a  command_a_b",
        "PRIVMSG Test :GROUP_B  command_b_a  command_b_b  command_b_c  command_b_d",
        "PRIVMSG Test :         command_b_e  command_b_f  command_b_g  command_b_h",
        "PRIVMSG Test :GROUP_C  command_c_a  command_c_b",
    )


def test_help_commands(mockbot, triggerfactory):
    provider = providers.Base()
    provider.setup(mockbot)

    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG #channel :.help')

    provider.help_commands(wrapper, wrapper._trigger)

    assert mockbot.backend.message_sent[0] == rawlist(
        "PRIVMSG #channel :Test: I'll send you a list of commands in private.",
    )[0]


def test_help_commands_private(mockbot, triggerfactory):
    provider = providers.Base()
    provider.setup(mockbot)

    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG %s :.help' % mockbot.nick)

    provider.help_commands(wrapper, wrapper._trigger)

    assert mockbot.backend.message_sent[0] == rawlist(
        "PRIVMSG Test :Here is my list of commands:",
    )[0]


def test_help_command(mockbot, triggerfactory):
    provider = providers.Base()
    provider.setup(mockbot)

    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG #channel :.help test')

    mockbot.doc['test'] = ([
            'The command test docstring.',
            'Second line of docstring.',
        ], [
            '.test', '.test arg', '.test else',
        ]
    )

    provider.help_command(wrapper, wrapper._trigger, 'test')

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG #channel :Test: The command test docstring.",
        "PRIVMSG #channel :Second line of docstring.",
        "PRIVMSG #channel :e.g. .test, .test arg or .test else",
    )


def test_help_command_private(mockbot, triggerfactory):
    provider = providers.Base()
    provider.setup(mockbot)

    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG TestBot :.help test')

    mockbot.doc['test'] = ([
            'The command test docstring.',
            'Second line of docstring.',
        ], [
            '.test', '.test arg', '.test else',
        ]
    )

    provider.help_command(wrapper, wrapper._trigger, 'test')

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG Test :The command test docstring.",
        "PRIVMSG Test :Second line of docstring.",
        "PRIVMSG Test :e.g. .test, .test arg or .test else",
    )


def test_help_command_too_long(mockbot, triggerfactory):
    """
    bot.reply('The documentation for this command is too long; '
                'I\'m sending it to you in a private message.')
    """
    provider = providers.Base()
    provider.setup(mockbot)

    wrapper = triggerfactory.wrapper(
        mockbot, ':Test!test@example.com PRIVMSG #channel :.help test')

    mockbot.doc['test'] = ([
            'The command test docstring.',
            'Second line of docstring.',
            'Third line of docstring.',
            'Fourth line of docstring.',
        ], [
            '.test', '.test arg', '.test else',
        ]
    )

    provider.help_command(wrapper, wrapper._trigger, 'test')

    assert mockbot.backend.message_sent == rawlist(
        "PRIVMSG #channel :Test: The help for this command is too long; "
        "I'm sending it to you in a private message.",
        "PRIVMSG Test :The command test docstring.",
        "PRIVMSG Test :Second line of docstring.",
        "PRIVMSG Test :Third line of docstring.",
        "PRIVMSG Test :Fourth line of docstring.",
        "PRIVMSG Test :e.g. .test, .test arg or .test else",
    )
