"""Sopel Help plugin"""
from sopel import config, module

from .managers import manager


def setup(bot):
    """Setup plugin."""
    bot.config.define_section('help', HelpSection)
    manager.setup(bot)


def configure(settings):
    """Configure plugin."""
    settings.define_section('help', HelpSection)
    provider_list = ', '.join(manager.provider_names)
    reply_method_list = ', '.join(HelpSection.REPLY_METHODS)
    settings.help.configure_setting(
        'output',
        'Pick a pastebin provider: {}: '.format(provider_list)
    )
    settings.help.configure_setting(
        'reply_method',
        'How/where should help command replies be sent: {}? '.format(
            reply_method_list)
    )


class HelpSection(config.types.StaticSection):
    """Configuration section for this module."""
    REPLY_METHODS = [
        'channel',
        'query',
        'notice',
    ]

    output = config.types.ChoiceAttribute('output',
                                          manager.provider_names,
                                          default='base')
    """The help provider to use for output."""
    reply_method = config.types.ChoiceAttribute('reply_method',
                                                REPLY_METHODS,
                                                default='channel')
    """Where/how to reply to help commands (public/private)."""


@module.commands('help')
@module.example('.help', user_help=True)
@module.example('.help help', user_help=True)
def sopel_help(bot, trigger):
    """Generate help for Sopel's commands."""
    if trigger.group(2):
        manager.provider.help_command(bot, trigger, trigger.group(2))
    else:
        manager.provider.help_commands(bot, trigger)
