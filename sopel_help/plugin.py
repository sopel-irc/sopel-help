"""Sopel Help plugin"""
from sopel import module

from .providers import Base


@module.commands('help')
@module.example('.help', user_help=True)
@module.example('.help help', user_help=True)
def sopel_help(bot, trigger):
    """Generate help for Sopel's commands."""
    base = Base()
    base.setup(bot)

    if trigger.group(2):
        base.help_command(bot, trigger, trigger.group(2))
    else:
        base.help_commands(bot, trigger)
