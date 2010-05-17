# check_webservice - a Nagios plugin for testing Webservices

A small plugin written in Python for testing Webservices.

You can set HTTP Headers, choose between a GET or POST request, and check the response with one or more Regular Expressions.

## Installation

Install the PyYAML library by downloading the last version from http://pyyaml.org/wiki/PyYAML

You'll need a config file. You can start with the default and tweak it to suit later:

    $ ./check_webservice.py -f example.conf

That's it - you can add this script to your Nagios installation and start testing Webservices.

See [http://levycarneiro.com](http://levycarneiro.com/) for more documentation.
