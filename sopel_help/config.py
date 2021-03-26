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

    origin_base_url = config.types.ValidatedAttribute(
        'origin_base_url',
        default='')
    """When using an origin server, what is the base URL to use."""

    origin_output_name = config.types.ValidatedAttribute(
        'origin_output_name',
        default='help.html')
    """How is named the file that will be used to store and publish content."""

    origin_output_dir = config.types.ValidatedAttribute(
        'origin_output_dir',
        default='/var/www/html')
    """Where the file will be put on the server to publish the content."""

    line_threshold = config.types.ValidatedAttribute(
        'line_threshold',
        default='3')
    """The maximum length (in lines) that the help for a specific command can be before it is sent in a private message."""
