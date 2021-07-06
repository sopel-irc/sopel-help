"""Mixins for providers."""
import html
import textwrap


class PlainTextGeneratorMixin:
    """Generator Mixin of plain text."""
    DEFAULT_WRAP_WIDTH = 70

    def get_wrap_width(self):
        """Get wrap width parameter."""
        return self.DEFAULT_WRAP_WIDTH

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
                text, width=self.get_wrap_width(), subsequent_indent=indent)
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


class HTMLGeneratorMixin(PlainTextGeneratorMixin):
    """Generator Mixin of HTML text."""
    def generate_help_commands(self, command_groups):
        """Generate help messages for a set of commands.

        :param dict command_groups: map of (category, commands)
        :return: generator of help text for each command group
        """
        for category, commands in sorted(command_groups.items()):
            # adjust category label to the max length

            title = html.escape(category)
            anchor = 'plugin-%s' % title.lower()

            lines = [
                '<h2 id="{anchor}">'
                '<a href="#{anchor}">{title}</a>'
                '</h2>'.format(anchor=anchor, title=title.upper()),
                '<ul>'
            ] + [
                '<li>%s</li>' % html.escape(command)
                for command in sorted(set(commands))
            ] + [
                '</ul>'
            ]
            yield ''.join(lines)
