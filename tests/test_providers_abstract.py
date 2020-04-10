import pytest

from sopel_help import providers


def test_generate_help_commands():
    abstract = providers.AbstractProvider()
    with pytest.raises(NotImplementedError):
        abstract.generate_help_commands([])


def test_send_help_commands():
    abstract = providers.AbstractProvider()
    with pytest.raises(NotImplementedError):
        abstract.send_help_commands(None, None, [])


def test_generate_help_command():
    abstract = providers.AbstractProvider()
    with pytest.raises(NotImplementedError):
        abstract.generate_help_command('test', [], [])
