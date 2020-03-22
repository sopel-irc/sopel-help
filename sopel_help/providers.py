"""Help providers."""
import textwrap


class AbstractProvider:
    """Help provider abstraction.

    A provider must implement these methods to be used as an Help Provider for
    the Help Sopel plugin.
    """
    def setup(self, bot):
        """Setup the provider with the bot's settings.

        This will be called at the plugin's setup stage. This can be used to
        store settings, declare custom sections, and so on.
        """
        raise NotImplementedError

    def help_commands(self, bot, trigger):
        """Handle triggered command to generate help for all commands."""
        raise NotImplementedError

    def help_command(self, bot, trigger, name):
        """Handle triggered command to generate help for one command."""
        raise NotImplementedError


class Base(AbstractProvider):
    """Base help provider for the help plugin.

    A provider can:

    * generate an help text for command groups,
    * generate an help info for one command (head, body, usages)
    """
    DEFAULT_WRAP_WIDTH = 70
    DEFAULT_THRESHOLD = 3

    def __init__(self):
        self.wrap_width = self.DEFAULT_WRAP_WIDTH
        self.threshold = self.DEFAULT_THRESHOLD

    def setup(self, bot):
        """There is no setup (yet)."""

    def help_commands(self, bot, trigger):
        lines = self.generate_help_commands(bot.command_groups)
        self.send_help_commands(bot, trigger, lines)

    def help_command(self, bot, trigger, name):
        command = name.strip().lower()
        recipient = trigger.sender
        reply = bot.reply
        is_private = trigger.nick == trigger.sender

        if is_private:
            reply = bot.say

        if command not in bot.doc:
            reply('Unknown command "%s"' % command)
            return

        docs, examples = bot.doc[command]
        head, body, usages = self.generate_help_command(
            command, docs, examples)

        message_length = len([head] + body) + int(bool(usages))
        if not is_private and message_length > self.threshold:
            reply(
                "The help for this command is too long; "
                "I'm sending it to you in a private message.")
            reply = bot.say
            recipient = trigger.nick

        reply(head, recipient)
        for line in body:
            bot.say(line, recipient)
        for line in usages:
            bot.say(line, recipient)

    def send_help_commands(self, bot, trigger, lines):
        """Send the list of commands in private message."""
        if trigger.sender != trigger.nick:
            bot.reply('I\'ll send you a list of commands in private.')
        else:
            bot.say('Here is my list of commands:', trigger.nick)

        for help_line in lines:
            for line in help_line.split('\n'):
                bot.say(line.rstrip(), trigger.nick)

    def generate_help_commands(self, command_groups):
        """Generate help messages for a set of commands.

        :param dict command_groups: map of (category, commands)
        :return: generator of help text for each command group
        """
        name_length = max(6, max(len(k) for k in command_groups.keys()))
        indent = ' ' * (name_length + 2)

        for category, commands in sorted(command_groups.items()):
            # adjust category label to the max length
            label = category.upper().ljust(name_length)
            text = '  '.join([label] + sorted(set(commands)))
            text_wrapped = textwrap.wrap(
                text, width=self.wrap_width, subsequent_indent=indent)
            yield '\n'.join(text_wrapped)

    def generate_help_command(self, command, docs, examples):
        """Generate help message with head, body, and usage examples.

        :param str command: command name, all lower-case
        :param list docs: list of documentation line for this ``command``
        :param list examples: list of examples for this ``command``
        :return: a 3-value tuple with (head, body, usages)

        The ``head`` is a string and it is the first line of the help message.
        The ``body`` is a list of help lines, and ``usages`` is a list of
        example lines.

        Note that ``usages`` contains one line only at the moment since we
        don't manage line length (yet).
        """
        head = 'Command "%s" has no help.' % command
        body = []
        usages = []

        if docs:
            # Head is the first line of doc, and the body contains the reminder
            head, *body = docs

        if examples:
            # Build a nice, grammatically-correct list of examples
            usage = ', '.join(examples[:-2] + [' or '.join(examples[-2:])])
            usages = ['e.g. %s' % usage]

        return head.strip(), body, usages


class AbstractPublisher(Base):
    """Abstract provider that publish doc on a pastebin-like service."""
    DEFAULT_WRAP_WIDTH = 70
    DEFAULT_THRESHOLD = 3
    DEFAULT_GROUP_SEPARATOR = '\n\n'

    def __init__(self):
        super().__init__()
        self.group_separator = self.DEFAULT_GROUP_SEPARATOR

    def send_help_commands(self, bot, trigger, lines):
        """Publish doc online and reply with the URL."""
        content = self.render(bot, trigger, lines)
        url = self.publish(bot, trigger, content)

        reply = bot.reply
        if trigger.sender == trigger.nick:
            reply = bot.say

        reply("I've published a list of my commands at: %s" % url)

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
