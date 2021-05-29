"""Sopel Help plugin"""
from sopel import module

from sopel_help import config, providers
from sopel_help.managers import manager


def setup(bot):
    """Setup plugin."""
    bot.config.define_section('help', config.HelpSection)
    manager.setup(bot)


def configure(settings):
    """Configure plugin."""
    settings.define_section('help', config.HelpSection)
    provider_list = ', '.join(manager.provider_names)
    reply_method_list = ', '.join(config.HelpSection.REPLY_METHODS)
    settings.help.configure_setting(
        'output',
        'Pick a pastebin provider: {}: '.format(provider_list)
    )
    settings.help.configure_setting(
        'reply_method',
        'How/where should help command replies be sent: {}? '.format(
            reply_method_list)
    )

    if settings.help.reply_method == 'channel':
        settings.help.configure_setting(
            'line_threshold',
            'How many lines can be sent in a channel for a command help '
            '(default 3)? '
        )

    manager.configure(settings)


@module.commands('help', 'h')
@module.example('.help', user_help=True)
@module.example('.help help', user_help=True)
def sopel_help(bot, trigger):
    """Generate help for Sopel's commands."""
    if trigger.group(2):
        try:
            manager.provider.help_command(bot, trigger, trigger.group(2))
        except providers.UnknownCommand as error:
            reply, recipient = manager.provider.get_reply_method(bot, trigger)
            reply(str(error), recipient)
    else:
        manager.provider.help_commands(bot, trigger)
