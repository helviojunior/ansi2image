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


def test_background_color_rendering():
    o = Ansi2Image(0, 0, font_name=Ansi2Image.get_default_font_name(), font_size=13)
    o.loads("\x1b[41mA\x1b[0m")
    o.calc_size(margin=0)

    png = o.generate_image(format='png')

    from PIL import Image
    img = Image.open(io.BytesIO(png))

    # top-left pixel belongs to first glyph background when margin is zero
    assert img.getpixel((0, 0)) == (194, 54, 33)
