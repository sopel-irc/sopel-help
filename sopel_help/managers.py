"""Sopel Help Managers."""

import pkg_resources

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
            entry_points = pkg_resources.iter_entry_points(
                PROVIDERS_ENTRY_POINT)
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

        The provider will be loaded from an entry point and then instanciated
        to be returned as is (no setup, no configure).
        """
        entry_points = pkg_resources.iter_entry_points(
            PROVIDERS_ENTRY_POINT, name)

        try:
            entry_point = next(entry_points)
        except StopIteration as err:
            raise RuntimeError('Cannot found help provider %s' % name) from err

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
