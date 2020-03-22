import pytest

from sopel_help import providers


def test_setup():
    abstract = providers.AbstractProvider()
    with pytest.raises(NotImplementedError):
        abstract.setup(None)


def test_help_commands():
    abstract = providers.AbstractProvider()
    with pytest.raises(NotImplementedError):
        abstract.help_commands(None, None)


def test_help_command():
    abstract = providers.AbstractProvider()
    with pytest.raises(NotImplementedError):
        abstract.help_command(None, None, None)
