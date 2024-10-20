"""Sopel Help Managers."""

import importlib_metadata

PROVIDERS_ENTRY_POINT = 'sopel_help.providers'


class Manager:
    """Manager of the Help provider."""
    @property
    def provider(self):
        """Help provider."""
        if self._provider is None:
            raise RuntimeError('Help provider is not configured yet.')
        return self._provider

    @property
    def provider_names(self):
        """Names of the available providers."""
        if self._provider_list is None:
            entry_points = importlib_metadata.entry_points(
                group=PROVIDERS_ENTRY_POINT)
            self._provider_list = [
                entry_point.name
                for entry_point in entry_points
            ]
        return self._provider_list

    def __init__(self):
        self._provider = None
        self._provider_list = None

    def load_provider(self, name):
        """Load provider from a name.

        :param str name: name of the provider
        :return: a provider instance
        :rtype: :class:`sopel_help.providers.AbstractProvider`

        The provider will be loaded from an entry point and then instantiated
        to be returned as is (no setup, no configure).
        """
        # 1. get EntryPoints matching the group and name
        entry_points = importlib_metadata.entry_points(
            group=PROVIDERS_ENTRY_POINT, name=name)

        # 2. get just the EntryPoint matching `name`
        try:
            entry_point = entry_points[name]
        except KeyError:
            raise RuntimeError('Cannot find help provider %r' % name) from None

        # 3. load the entry point
        provider_maker = entry_point.load()

        return provider_maker()

    def setup(self, bot):
        """Setup the manager from the bot's settings.

        The goal of the setup phase is to fetch the right provider based on the
        settings provided, load the entry point, setup the provider, and store
        it so :attr:`provider` is available.
        """
        # 1. get bot's settings's help section's "provider" option
        name = bot.settings.help.output

        # 2. load the proper provider
        provider = self.load_provider(name)

        # 3. setup the provider
        provider.setup(bot)

        # 4. store it
        self._provider = provider

    def configure(self, settings):
        """Configure the provider from the settings."""
        # 1. get settings's help section's "provider" option
        name = settings.help.output

        # 2. load the proper provider
        provider = self.load_provider(name)

        # 3. configure it
        provider.configure(settings)


manager = Manager()  # pylint: disable=invalid-name
