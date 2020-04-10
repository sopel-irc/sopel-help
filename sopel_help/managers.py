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

    def setup(self, bot):
        """Setup the manager from the bot's settings.

        The goal of the setup phase is to fetch the right provider based on the
        settings provided, load the entry point, setup the provider, and store
        it so :attr:`provider` is available.
        """
        # 1. get bot's settings's help section's "provider" option
        name = bot.settings.help.output

        # 2. get the proper provider entrypoint
        entry_points = pkg_resources.iter_entry_points(
            PROVIDERS_ENTRY_POINT, name)

        try:
            entry_point = next(entry_points)
        except StopIteration:
            raise RuntimeError('Cannot found help provider %s' % name)

        # 3. load the entry point
        provider_maker = entry_point.load()
        provider = provider_maker()

        # 4. setup the provider
        provider.setup(bot)

        # 5. store it
        self._provider = provider


manager = Manager()  # pylint: disable=invalid-name