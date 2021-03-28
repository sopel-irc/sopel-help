==========
sopel-help
==========

Sopel plugin ``.help`` command::

    [Exirel]: .help help
    [Sopel]: Generate help for Sopel's commands.
    [Sopel]: e.g. .help help or .help

Install
=======

The recommanded way to install this plugin is to use ``pip``::

    $ pip install sopel-help

Note that this plugin requires Python 3.5+ and Sopel 7+.

Configure
=========

As with many other plugins, you can use ``sopel-config`` to launch the
configuration wizard, like so::

    $ sopel-plugins configure help

Don't forget to use the ``-c <config-name>`` option to select the right config.

Providers
=========

There are several providers built-in with this plugin:

* ``base`` (the default): basic provider; it outputs help directly to the user
* ``local``: it generates an HTML file and outputs an URL; you have to
  install and configure your own origin server to serve that file
* ``clbin``, ``0x0``, ``hastebin``, ``termbin``, ``ubuntu``: all these
  providers post a plain-text file to a pastebin service and then output the
  resulting URL
