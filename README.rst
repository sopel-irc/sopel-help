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

Providers
=========

There are several providers built-in with this plugin:

* ``base`` (the default): basic provider; it outputs help directly to the user
* ``local``: it generates an HTML file and outputs an URL; you have to
  install and configure your own origin server to serve that file
* ``clbin``, ``0x0``, ``hastebin``, ``termbin``, ``ubuntu``: all these
  providers post a plain-text file to a pastebin service and then output the
  resulting URL
