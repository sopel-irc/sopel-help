"""Configuration for the help plugin."""
from sopel import config

from sopel_help.managers import manager


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
