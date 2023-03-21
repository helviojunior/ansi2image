#reference: https://medium.com/assertqualityassurance/tutorial-de-pytest-para-iniciantes-cbdd81c6d761
import codecs
import datetime

import pytest, sys
import io

from ansi2image.ansi2image import Ansi2Image
from ansi2image.config import Configuration
from ansi2image.libs.color import Color
from ansi2image.libs.logger import Logger


def test_read_file():
    sys.argv = ['ansi2image', 'setup.py', '-o', 'teste.png']
    Configuration.initialize()

    Color.pl(Configuration.get_banner())

    o = Ansi2Image(Configuration.size[0], Configuration.size[1], font_name=Configuration.font.name, font_size=13)

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Logger.pl('{+} {C}Start time {O}%s{W}' % timestamp)

    try:

        if Configuration.filename == '-':
            o.load(io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8'))
        else:
            o.load_from_file(Configuration.filename)

        o.calc_size()
        o.save_image(Configuration.out_file, format=Configuration.format)

        assert True
        #sys.exit(0)
    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        Color.pl('\n{!} {O}Full stack trace below')
        from traceback import format_exc
        Color.p('\n{!}    ')
        err = format_exc().strip()
        err = err.replace('\n', '\n{W}{!} {W}   ')
        err = err.replace('  File', '{W}{D}File')
        err = err.replace('  Exception: ', '{R}Exception: {O}')
        Color.pl(err)

        Color.pl('\n{!} {R}Exiting{W}\n')

        assert False
