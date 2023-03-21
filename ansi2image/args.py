#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from argparse import _ArgumentGroup, Namespace
from .libs.color import Color

import argparse, sys, os


class Arguments(object):
    ''' Holds arguments used by the ansi2image '''
    modules = {}
    verbose = False
    args = None

    def __init__(self):
        self.verbose = any(['-v' in word for word in sys.argv])
        self.args = self.get_arguments()

    def _verbose(self, msg):
        if self.verbose:
            Color.pl(msg)

    def get_arguments(self) -> Namespace:
        ''' Returns parser.args() containing all program arguments '''

        parser = argparse.ArgumentParser(
            usage=argparse.SUPPRESS,
            prog="ansi2image",
            add_help=False,
            formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=180))

        parser.add_argument('filename',
                            action='store',
                            metavar='[filename]',
                            type=str,
                            help=Color.s('File path or {G}-{W} to stdin'))

        flags = parser.add_argument_group('Options')
        self._add_flags_args(flags)

        return parser.parse_args()

    def _add_flags_args(self, flags: _ArgumentGroup):
        flags.add_argument('-o' '--output',
                           action='store',
                           metavar='[filename]',
                           type=str,
                           dest=f'out_file',
                           help=Color.s('image output file.'))

        flags.add_argument('--font',
                           action='store',
                           metavar='[font]',
                           type=str,
                           default='JetBrains Mono Regular',
                           dest=f'font',
                           help=Color.s('font type. (default: {G}JetBrains Mono Regular{W}).'))

        flags.add_argument('--font-list',
                           action='store_true',
                           default=False,
                           dest=f'font_list',
                           help=Color.s('List all supported font family and variations'))

        flags.add_argument('-h', '--help',
                           action='help',
                           help=Color.s('show help message and exit'))

        flags.add_argument('-v',
                           action='count',
                           default=0,
                           help=Color.s(
                               'Specify verbosity level (default: {G}0{W}). Example: {G}-v{W}, {G}-vv{W}, {G}-vvv{W}'
                           ))

        flags.add_argument('--version',
                           action='store_true',
                           default=False,
                           dest=f'version',
                           help=Color.s('show current version'))
