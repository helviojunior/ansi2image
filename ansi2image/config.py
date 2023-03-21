#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import errno
import os, sys
import re
from pathlib import Path
from typing import Optional

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from .fonts.truetypefont import TrueTypeFont
from .libs.color import Color
from .libs.logger import Logger
from .__meta__ import __version__, __description__

_FORMATS = ['jpg', 'jpeg', 'png']


class Configuration(object):
    ''' Stores configuration variables and functions for Tfileindexer. '''
    version = '0.0.0'
    name = ""

    initialized = False # Flag indicating config has been initialized
    verbose = 0
    filename = None
    cmd_line = ''
    format = None
    fonts = []
    font = None
    size = (700, 300)
    out_file = None

    @staticmethod
    def initialize():
        '''
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        '''

        Configuration.version = str(__version__)
        Configuration.name = "ANSI2Image"

        # Only initialize this class once
        if Configuration.initialized:
            return

        Configuration.initialized = True

        Configuration.verbose = 0 # Verbosity level.
        Configuration.print_stack_traces = True

        # Overwrite config values with arguments (if defined)
        Configuration.load_from_arguments()

    @staticmethod
    def count_file_lines(filename: str):
        def _count_generator(reader):
            b = reader(1024 * 1024)
            while b:
                yield b
                b = reader(1024 * 1024)

        with open(filename, 'rb') as fp:
            c_generator = _count_generator(fp.raw.read)
            # count each \n
            count = sum(buffer.count(b'\n') for buffer in c_generator)
            return count + 1

    @staticmethod
    def list_fonts():
        for f in Configuration.fonts:
            Color.pl('{+} {W}Font Family: {O}%s{W}' % f['name'])
            for v in f['variation']:
                Color.pl('     {W}- {GR}%s{W}' % v['name'])
        print(' ')

    @staticmethod
    def load_from_arguments():
        ''' Sets configuration values based on Argument.args object '''
        from .args import Arguments

        Configuration.fonts = TrueTypeFont.load_fonts()

        if any(['--version' in word for word in sys.argv]):
            Logger.pl(f' {Configuration.name} v{Configuration.version}\n')
            sys.exit(0)

        if any(['--font-list' in word for word in sys.argv]):
            Configuration.list_fonts()
            sys.exit(0)

        args = Arguments()

        a1 = sys.argv
        a1[0] = 'ansi2image'
        for a in a1:
            Configuration.cmd_line += "%s " % a

        Configuration.verbose = args.args.v
        Configuration.filename = args.args.filename

        if Configuration.filename is None or Configuration.filename.strip() == '':
            Logger.pl('{!} {R}error: filename is invalid {O}%s{R} {W}\r\n' % (
                args.args.config_file))
            exit(1)

        if Configuration.filename != '-' and not os.path.isfile(Configuration.filename):
            Logger.pl('{!} {R}error: filename does not exists {O}%s{R} {W}\r\n' % (
                Configuration.filename))
            exit(1)

        if args.args.out_file is None or args.args.out_file.strip() == '' or os.path.isdir(args.args.out_file):
            Logger.pl('{!} {R}error: invalid output filename {O}%s{R} {W}\r\n' % (
                args.args.out_file))
            exit(1)

        Configuration.out_file = args.args.out_file

        try:
            if Configuration.filename != '-':
                with open(Configuration.filename, 'r') as f:
                    # file opened for writing. write to it here
                    pass
        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}Error: could not open file {O}permission denied{R}{W}\r\n')
                sys.exit(1)
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}Error: could not open file {O}it is an directory{R}{W}\r\n')
                sys.exit(1)
            else:
                Logger.pl('{!} {R}Error: could not openfile {W}\r\n')
                sys.exit(1)

        fmt = Path(Configuration.out_file).suffix.strip('. ').lower()

        if fmt is None or fmt not in _FORMATS:
            Logger.pl('{!} {R}error: invalid image format {O}%s{R}. Supported formats: {G}%s{W}\r\n' % (
                fmt, ', '.join(_FORMATS)))
            exit(1)

        Configuration.format = fmt.lower()
        if Configuration.format == 'jpg':
            Configuration.format = 'jpeg'

        try:
            Configuration.font = TrueTypeFont(args.args.font)
        except:
            Logger.pl(
                '{!} {R}Error selecting font {O}%s{R}{W}\n     {W}{D}Check available fonts with {G}--font-list{W}' %
                args.args.font, out=sys.stderr)
            sys.exit(1)

        Color.pl('{+} {W}Startup parameters')
        Logger.pl('     {C}command line:{O} %s{W}' % Configuration.cmd_line)
        Logger.pl('     {C}font:{O} %s{W}' % Configuration.name)

    @staticmethod
    def get_banner():
            Configuration.version = str(__version__)

            return '''\

{G}ANSI to image {D}v%s{W}{G} by Helvio Junior{W}
{W}{D}%s{W}
{C}{D}https://github.com/helviojunior/ansi2image{W}
    ''' % (Configuration.version, __description__)
