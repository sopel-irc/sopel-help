"""Help providers."""
import hashlib
import os
import socket
import urllib

import requests
from sopel.tools import get_logger

from sopel_help import mixins

LOGGER = get_logger('help')


class PublishingError(Exception):
    """Generic publishing error."""


class UnknownCommand(Exception):
    """Command is unknown."""


def _post_content(*args, **kwargs):
    try:
        response = requests.post(*args, **kwargs)
        response.raise_for_status()
    except (
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError
    ) as err:
        # We re-raise all expected exception types to a generic "posting error"
        # that's easy for callers to expect, and then we pass the original
        # exception through to provide some debugging info
        LOGGER.exception('Error during POST request')
        raise PublishingError(
            'Could not communicate with publishing service'
        ) from err

    # successful response is left to the caller to handle
    return response


class AbstractProvider:
    """Help provider abstraction.

    A provider must implement these methods to be used as an Help Provider:

    * :meth:`help_commands`: provide a list of all commands
    * :meth:`help_command`: provide help for one command
    """
    def setup(self, bot):
        """Setup the provider with the bot's settings.

        This will be called at the plugin's setup stage. This can be used to
        store settings, declare custom sections, and so on.

        By default this a no-op method.
        """

    def configure(self, settings):
        """Configure the bot's settings for this provider.

        By default this a no-op method.
        """

    def help_commands(self, bot, trigger):
        """Handle triggered command to generate help for all commands."""
        raise NotImplementedError

    def help_command(self, bot, trigger, name):
        """Handle triggered command to generate help for one command."""
        raise NotImplementedError


class AbstractGeneratedProvider(AbstractProvider):
    """Help provider that generate help content for the user on the fly.

    This abstract provider implements a workflow for the list of commands and
    the help for one command. Subclasses must implement these methods:

    * :meth:`generate_help_commands`: generate lines of help message from
      command groups
    * :meth:`send_help_commands`: send the lines of help to the user
    * :meth:`generate_help_command`: generate a header, a list of body lines,
      and a list of usage lines for one command

    This abstract provider already implements the :meth:`send_help_command`
    that sends the head/body/usage to the user.
    """
    def generate_help_commands(self, command_groups):
        """Generate help messages for a set of commands.

        :param dict command_groups: map of (category, commands)
        :return: generator of help data for each command group
        """
        raise NotImplementedError

    def send_help_commands(self, bot, trigger, lines):
        """Reply to the user with the help for all commands.

        :param bot: Wrapped bot object
        :type bot: :class:`sopel.bot.SopelWrapper`
        :param trigger: Trigger to reply to
        :type: :class:`sopel.trigger.Trigger`
        :param list lines: lines of help
        """
        raise NotImplementedError

    def generate_help_command(self, command, docs, examples):
        """Generate help message with head, body, and usage examples.

        :param str command: command name, all lower-case
        :param list docs: list of documentation line for this ``command``
        :param list examples: list of examples for this ``command``
        :return: a 3-value tuple with (head, body, usages)
        """
        raise NotImplementedError

    def send_help_command(self, bot, trigger, command, head, body, usages):
        """Reply to the user with the help for one command.

        :param bot: Wrapped bot object
        :type bot: :class:`sopel.bot.SopelWrapper`
        :param trigger: Trigger to reply to
        :type: :class:`sopel.trigger.Trigger`
        :param str head: head message for this command
        :param list body: body lines
        :param list usages: usage lines
        """
        reply, recipient = self.get_reply_method(bot, trigger)
        message_length = len([head] + body) + int(bool(usages))

        # check if help message is too long for a channel
        too_long = message_length > bot.settings.help.line_threshold
        if recipient != trigger.nick and too_long:
            reply(
                "The help for command %s is too long; "
                "I'm sending it to you in a private message." % command)
            reply = bot.say
            recipient = trigger.nick

        reply(head, recipient)
        for line in body:
            bot.say(line, recipient)
        for line in usages:
            bot.say(line, recipient)

    def get_reply_method(self, bot, trigger):
        """Define the reply method and its recipient.

        :param bot: Wrapped bot object
        :type bot: :class:`sopel.bot.SopelWrapper`
        :param trigger: Trigger to reply to
        :type: :class:`sopel.trigger.Trigger`
        """
        reply = bot.reply
        recipient = trigger.sender

        if trigger.is_privmsg or bot.settings.help.reply_method == 'query':
            reply = bot.say
            recipient = trigger.nick
        elif bot.settings.help.reply_method == 'notice':
            reply = bot.notice
            recipient = trigger.nick

        return reply, recipient

    def get_command_doc(self, bot, name):
        """Retrieve the command, its description and list of examples."""
        command = name.strip().lower()

        if command not in bot.doc:
            raise UnknownCommand('Unknown command "%s"' % command)

        return [command] + list(bot.doc[command])

    def help_commands(self, bot, trigger):
        """Handle triggered command to generate help for all commands."""
        lines = self.generate_help_commands(bot.command_groups)
        self.send_help_commands(bot, trigger, lines)

    def help_command(self, bot, trigger, name):
        """Handle triggered command to generate help for one command."""
        command, docs, examples = self.get_command_doc(bot, name)
        head, body, usages = self.generate_help_command(
            command, docs, examples)
        self.send_help_command(bot, trigger, command, head, body, usages)


class Base(mixins.PlainTextGeneratorMixin, AbstractGeneratedProvider):
    """Base help provider for the help plugin."""
    def send_help_commands(self, bot, trigger, lines):
        """Send the list of commands in private message."""
        reply, recipient = self.get_reply_method(bot, trigger)
        if trigger.is_privmsg:
            reply('Here is my list of commands:', recipient)
        else:
            reply('I\'ll send you a list of commands in private.', recipient)

        for help_line in lines:
            for line in help_line.split('\n'):
                bot.say(line.rstrip(), trigger.nick)


class LocalFile(mixins.HTMLGeneratorMixin, AbstractGeneratedProvider):
    """Local Server provider for the help plugin.

    This provider generate an HTML file on the filesystem and send a URL to
    the user. This URL is built on the setting ``help.origin_base_url``
    and ``help.origin_output_name``.

    So for instance if the origin base URL is ``http://example.com/sopel/`` and
    the origin output name is ``help.html``, the result will looks like this::

        [13:37] Sopel: I've published a list of my commands at
                       http://example.com/sopel/help.html

    You can control these with:

    * ``help.origin_base_url``: base URL
    * ``help.origin_output_name``: name of the HTML file
    * ``help.origin_output_dir``: local directory to publish the file

    Then you have to configure an origin server that can serve this HTML file,
    like apache, nginx, or lighttpd.
    """
    def __init__(self):
        super().__init__()
        self.base_url = None
        self.output_name = None
        self.output_dir = None

    def setup(self, bot):
        self.base_url = bot.settings.help.origin_base_url
        self.output_name = bot.settings.help.origin_output_name
        self.output_dir = bot.settings.help.origin_output_dir

    def configure(self, settings):
        """Configure the bot's settings for this provider.

        Allow the user to configure these:

        * ``help.origin_base_url``
        * ``help.origin_output_name``
        * ``help.origin_output_dir``
        """
        settings.help.configure_setting(
            'origin_base_url',
            'What is the base URL for the origin server?'
        )
        settings.help.configure_setting(
            'origin_output_name',
            'What is name of the help file to be generated?'
        )
        settings.help.configure_setting(
            'origin_output_dir',
            'Where to put the help file? (directory)'
        )

    def save_content(self, content):
        """Save ``content`` to the output dir.

        :param str content: HTML content to save to a local directory
        :return: the name of the file
        :rtype: str

        You can control:

        * ``help.origin_output_name``: name of the HTML file
        * ``help.origin_output_dir``: local directory to publish the file

        Note that if the file already exists, its content will be replaced.
        """
        filename = os.path.join(self.output_dir, self.output_name)
        with open(filename, 'w') as helpfd:
            helpfd.write(content)

        return self.output_name

    def render(self, bot, trigger, lines):  # pylint: disable=unused-argument
        """Render ``lines`` as an HTML document.

        :param bot: Wrapped bot object
        :type bot: :class:`sopel.bot.SopelWrapper`
        :param trigger: Trigger to reply to
        :type: :class:`sopel.trigger.Trigger`
        :param list lines: lines of help
        """
        template = """<!DOCTYPE html>
        <html>
            <head>
                <title>Sopel Help</title>
                <meta charset="utf-8">
            </head>
            <body>
            <h1>Sopel Help</h1>
            {content}
            </body>
        </html>
        """

        content = '\n'.join(
            '<div>%s</div>' % line
            for line in lines
        )

        return template.format(content=content)

    def send_help_commands(self, bot, trigger, lines):
        content = self.render(bot, trigger, lines)
        filename = self.save_content(content)
        url = urllib.parse.urljoin(self.base_url, filename)

        reply, recipient = self.get_reply_method(bot, trigger)
        reply("I've published a list of my commands at: %s" % url, recipient)


class AbstractPublisher(mixins.PlainTextGeneratorMixin,
                        AbstractGeneratedProvider):
    """Abstract provider that publish doc on a pastebin-like service."""
    DEFAULT_WRAP_WIDTH = 70
    DEFAULT_THRESHOLD = 3
    DEFAULT_GROUP_SEPARATOR = '\n\n'

    def __init__(self):
        super().__init__()
        self.group_separator = self.DEFAULT_GROUP_SEPARATOR
        self._cached_value = None
        self._cached_signature = None

    def get_cached_value(self, signature):
        """Get the cached value from the given ``signature``.

        :param str signature: cache signature
        :return: the cached value if the signature is still valid;
                 ``None`` otherwise
        """
        if signature != self._cached_signature:
            return None

        return self._cached_value

    def get_cache_signature(self, bot, trigger, content):
        """Generate a cache signature from given parameters.

        :param bot: Sopel bot
        :param trigger: Trigger line
        :param str content: Help content to sign

        The cache signature is derived from:

        * bot's settings (choosen output)
        * current content
        * date of the trigger, to rotate cache every day

        Then it uses a basic sha1 algorithm to sign it all.
        """
        payload = (
            ('output', bot.settings.help.output),
            ('content', content),
            ('date', trigger.time.date().isoformat()),
        )
        hasher = hashlib.sha1()
        for key, value in payload:
            # create "key:value" line to update
            line = '%s:%s\n' % (key, value.replace(':', '\\:'))
            hasher.update(line.encode('utf-8'))

        return hasher.hexdigest()

    def save_cache(self, signature, value):
        """Save the generated URL with its signature.

        :param str signature: cache signature
        :param str value: value to cache
        """
        self._cached_value = value
        self._cached_signature = signature

    def send_help_commands(self, bot, trigger, lines):
        """Publish doc online and reply with the URL."""
        content = self.render(bot, trigger, lines)

        signature = self.get_cache_signature(bot, trigger, content)
        url = self.get_cached_value(signature)

        # if cached URL doesn't exist or is invalid, let's generate a new one
        if not url:
            url = self.publish(bot, trigger, content)
            self.save_cache(signature, url)

        reply, recipient = self.get_reply_method(bot, trigger)
        reply("I've published a list of my commands at: %s" % url, recipient)

    def render(self, bot, trigger, lines):  # pylint: disable=unused-argument
        """Render document lines as a single text document."""
        return self.group_separator.join(lines)

    def publish(self, bot, trigger, content):
        """Publish the content to an online service and return the URL.

        :param bot: Sopel wrapper
        :param trigger: Trigger for this help command
        :param str content: Content to publish online
        :return: The URL to access the published content
        :rtype: str
        """
        raise NotImplementedError


class CLBinPublisher(AbstractPublisher):
    """Publishing provider using clbin.com"""
    def publish(self, bot, trigger, content):
        response = _post_content('https://clbin.com/', data={
            'clbin': content
        })
        return response.text.strip()


class NullPointerPublisher(AbstractPublisher):
    """Publishing provider using 0x0.st"""
    def publish(self, bot, trigger, content):
        response = _post_content('https://0x0.st/', data={
            'file': content
        })
        return response.text.strip()


class HasteBinPublisher(AbstractPublisher):
    """Publishing provider using hastebin.com"""
    def publish(self, bot, trigger, content):
        response = _post_content('https://hastebin.com/documents', data={
            'data': content
        })

        try:
            result = response.json()
        except ValueError as err:
            LOGGER.error("Invalid Hastebin response %s", response.text)
            raise PublishingError(
                'Could not parse response from Hastebin!'
            ) from err

        try:
            key = result['key']
        except KeyError as err:
            LOGGER.error("Invalid Hastebin JSON: %s", result)
            raise PublishingError(
                'Could not parse response from Hastebin!'
            ) from err

        return "https://hastebin.com/%s" % key


class TermBinPublisher(AbstractPublisher):
    """Publishing provider using termbin.com"""
    def publish(self, bot, trigger, content):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # the bot may NOT wait forever for a response; that would be bad
        sock.settimeout(10)
        try:
            sock.connect(('termbin.com', 9999))
            sock.sendall(content)
            sock.shutdown(socket.SHUT_WR)
            response = ""
            while 1:
                data = sock.recv(1024)
                if data == "":
                    break
                response += data
            sock.close()
        except socket.error as err:
            LOGGER.exception('Error during communication with termbin')
            raise PublishingError('Error uploading to termbin') from err

        return response


class UbuntuPublisher(AbstractPublisher):
    """Publishing provider using pastebin.ubuntu.com"""
    def publish(self, bot, trigger, content):
        ubuntu_url = 'https://pastebin.ubuntu.com/'
        response = _post_content(ubuntu_url, data={
            'poster': 'sopel',
            'syntax': 'text',
            'expiration': '',
            'content': content,
        }, allow_redirects=False)
        location = response.headers['Location']
        return urllib.parse.urljoin(ubuntu_url, location)
