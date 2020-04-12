import pytest
from sopel import config

from sopel_help import managers, providers

TMP_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable = coretasks, help

[help]
output = base
"""


@pytest.fixture
def tmpconfig(configfactory):
    return configfactory('test.cfg', TMP_CONFIG)


@pytest.fixture
def mockbot(tmpconfig, botfactory):
    return botfactory.preloaded(tmpconfig, preloads=['help'])


def test_provider_error():
    manager = managers.Manager()

    with pytest.raises(RuntimeError):
        manager.provider


def test_setup(mockbot):
    manager = managers.Manager()
    manager.setup(mockbot)

    assert isinstance(manager.provider, providers.AbstractProvider)


def test_provider_names():
    manager = managers.Manager()

    assert 'base' in manager.provider_names
    assert 'local' in manager.provider_names
    assert 'clbin' in manager.provider_names
    assert '0x0' in manager.provider_names
    assert 'hastebin' in manager.provider_names
    assert 'termbin' in manager.provider_names
    assert 'ubuntu' in manager.provider_names


def test_setup_invalid_provider(tmpconfig, botfactory):
    class MockHelpSection(config.types.StaticSection):
        output = config.types.ValidatedAttribute('output', str, default='base')

    mockbot = botfactory(tmpconfig)
    mockbot.settings.define_section('help', MockHelpSection)
    mockbot.settings.help.output = 'invalid'
    manager = managers.Manager()

    with pytest.raises(RuntimeError):
        manager.setup(mockbot)
