#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import datetime
import io
import json
import re
from typing import Iterator, Union, List, Optional, Tuple
from PIL import Image, ImageDraw
from PIL.ImageFont import FreeTypeFont

from .fonts.truetypefont import TrueTypeFont
from .libs.logger import Logger
import colorama
colorama.init(strip=False)

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ansi2image from the root directory (which includes README.md)', e)

import sys, os
from .libs.color import Color

# Based on https://en.wikipedia.org/wiki/_ANSI_escape_code#Escape_sequences
_ANSI_SEQUENCES = re.compile(r'''
    \x1B            # Sequence starts with ESC, i.e. hex 0x1B
    (?:
        [@-Z\\-_]   # Second byte:
                    #   all 0x40–0x5F range but CSI char, i.e ASCII @A–Z\]^_
    |               # Or
        \[          # CSI sequences, starting with [
        [0-?]*      # Parameter bytes:
                    #   range 0x30–0x3F, ASCII 0–9:;<=>?
        [ -/]*      # Intermediate bytes:
                    #   range 0x20–0x2F, ASCII space and !"#$%&'()*+,-./
        [@-~]       # Final byte
                    #   range 0x40–0x7E, ASCII @A–Z[\]^_`a–z{|}~
    )
''', re.VERBOSE)

_ANSI_CODES_PROG = re.compile("\033\\[([\\d;:]*)([a-zA-z])")

_ANSI_FULL_RESET = 0
_ANSI_INTENSITY_INCREASED = 1
_ANSI_INTENSITY_REDUCED = 2
_ANSI_INTENSITY_NORMAL = 22
_ANSI_STYLE_ITALIC = 3
_ANSI_STYLE_NORMAL = 23
_ANSI_BLINK_SLOW = 5
_ANSI_BLINK_FAST = 6
_ANSI_BLINK_OFF = 25
_ANSI_UNDERLINE_ON = 4
_ANSI_UNDERLINE_OFF = 24
_ANSI_CROSSED_OUT_ON = 9
_ANSI_CROSSED_OUT_OFF = 29
_ANSI_VISIBILITY_ON = 28
_ANSI_VISIBILITY_OFF = 8
_ANSI_FOREGROUND = 38
_ANSI_FOREGROUND_DEFAULT = 39
_ANSI_BACKGROUND = 48
_ANSI_BACKGROUND_DEFAULT = 49
_ANSI_NEGATIVE_ON = 7
_ANSI_NEGATIVE_OFF = 27
_ANSI_256_COLOR_ID = 5
_ANSI_TRUECOLOR_ID = 2

_BACKGROUND_COLOR = (0, 0, 0)
_FOREGROUND_COLOR = (240, 240, 240)

#https://en.wikipedia.org/wiki/_ANSI_escape_code#3-bit_and_4-bit
_ANSI_COLORS = {
    #Black
    30:     (_ANSI_FOREGROUND, 0, 0, 0),
    40:     (_ANSI_BACKGROUND, 0, 0, 0),

    # Red
    31: (_ANSI_FOREGROUND, 194, 54, 33),
    41: (_ANSI_BACKGROUND, 194, 54, 33),

    # Green
    32: (_ANSI_FOREGROUND, 37, 188, 36 ),
    42: (_ANSI_BACKGROUND, 37, 188, 36 ),

    # Yellow
    33: (_ANSI_FOREGROUND, 173, 173, 39),
    43: (_ANSI_BACKGROUND, 173, 173, 39),

    # Blue
    34: (_ANSI_FOREGROUND, 0, 0, 187),
    44: (_ANSI_BACKGROUND, 0, 0, 187),

    # Magenta
    35: (_ANSI_FOREGROUND, 211, 56, 211),
    45: (_ANSI_BACKGROUND, 211, 56, 211),

    # Cyan
    36: (_ANSI_FOREGROUND, 0, 187, 187),
    46: (_ANSI_BACKGROUND, 0, 187, 187),

    # White
    37: (_ANSI_FOREGROUND, 187, 187, 187),
    47: (_ANSI_BACKGROUND, 187, 187, 187),

    # Bright Black (Gray)
    90: (_ANSI_FOREGROUND, 85, 85, 85),
    100: (_ANSI_BACKGROUND,85, 85, 85),

    # Bright Red
    91: (_ANSI_FOREGROUND, 255, 85, 85),
    101: (_ANSI_BACKGROUND, 255, 85, 85),

    # Bright Green
    92: (_ANSI_FOREGROUND, 85, 255, 85),
    102: (_ANSI_BACKGROUND, 85, 255, 85),

    # Bright Yellow
    93: (_ANSI_FOREGROUND, 255, 255, 85),
    103: (_ANSI_BACKGROUND, 255, 255, 85),

    # Bright Blue
    94: (_ANSI_FOREGROUND, 85, 85, 255),
    104: (_ANSI_BACKGROUND, 85, 85, 255),

    # Bright Magenta
    95: (_ANSI_FOREGROUND, 255, 85, 255),
    105: (_ANSI_BACKGROUND, 255, 85, 255),

    # Bright Cyan
    96: (_ANSI_FOREGROUND, 85, 255, 255),
    106: (_ANSI_BACKGROUND, 85, 255, 255),

    # Bright White
    97: (_ANSI_FOREGROUND, 255, 255, 255),
    107: (_ANSI_BACKGROUND, 255, 255, 255),

}

#https://www.ditig.com/downloads/256-colors.json
here = os.path.abspath(os.path.dirname(__file__))
_ANSI_256_COLORS = json.load(open(f'{here}/libs/256-colors.json', 'r'))


class Ansi2Image(object):
    '''
    Parse ANSI escape codes
    Reference: https://en.wikipedia.org/wiki/_ANSI_escape_code
    '''
    lines = []
    width = 0
    height = 0
    font_size = 20
    margin = 10
    line_height = 1.2
    font_name = 'JetBrains Mono Regular'
    _background_color = None
    _foreground_color = None

    class TextColor(object):
        _background_color = None
        _foreground_color = None
        _background = None
        _foreground = None
        _text = None
        _intensity = _ANSI_INTENSITY_NORMAL
        _style = _ANSI_STYLE_NORMAL
        _underline = _ANSI_UNDERLINE_OFF
        _visibility = _ANSI_VISIBILITY_ON
        _negative = _ANSI_NEGATIVE_OFF

        def __init__(self, text: str = '', foreground=None, background=None):
            self._text = text
            self._background = background if not None else Ansi2Image._background_color
            self._foreground = foreground if not None else Ansi2Image._foreground_color

            self.reset()

        @property
        def text(self) -> str:
            if self._visibility == _ANSI_VISIBILITY_OFF:
                return ' ' * len(self._text)
            return self._text

        @property
        def background_color(self) -> Tuple[int]:
            if self._negative == _ANSI_NEGATIVE_ON:
                return self._intensity_color(self._foreground_color)
            return self._intensity_color(self._background_color)

        @property
        def foreground_color(self) -> Tuple[int]:
            if self._negative == _ANSI_NEGATIVE_ON:
                return self._intensity_color(self._background_color)
            return self._intensity_color(self._foreground_color)

        def _intensity_color(self, color: Tuple[int]) -> Tuple[int]:
            if color is None:
                return None
            if self._intensity in (_ANSI_INTENSITY_NORMAL, _ANSI_INTENSITY_INCREASED):
                return color
            else:
                base_img = Image.new("RGB", (6, 6), self._foreground)
                drw = ImageDraw.Draw(base_img, 'RGBA')
                drw.polygon(xy=[(0, 0), (6, 6)], fill=color + (200,))
                del drw
                r, g, b = base_img.getpixel((3, 3))
                return r, g, b

        def set_color(self, ansi_code: int, r: int, g: int, b: int) -> None:
            if ansi_code == _ANSI_FOREGROUND:
                self._foreground_color = (r, g, b)
            else:
                self._background_color = (r, g, b)

        def adjust(self, ansi_code: int, parameter: Optional[str] = None) -> None:
            if ansi_code in (
                    _ANSI_INTENSITY_INCREASED,
                    _ANSI_INTENSITY_REDUCED,
                    _ANSI_INTENSITY_NORMAL,
            ):
                self._intensity = ansi_code
            elif ansi_code in (_ANSI_STYLE_ITALIC, _ANSI_STYLE_NORMAL):
                self._style = ansi_code
            elif ansi_code in (_ANSI_UNDERLINE_ON, _ANSI_UNDERLINE_OFF):
                self._underline = ansi_code
            elif ansi_code in (_ANSI_VISIBILITY_ON, _ANSI_VISIBILITY_OFF):
                self._visibility = ansi_code
            elif ansi_code in (_ANSI_NEGATIVE_ON, _ANSI_NEGATIVE_OFF):
                self._negative = ansi_code
            elif ansi_code in _ANSI_COLORS.keys():
                # 3-bit and 4-bit colors
                c = _ANSI_COLORS.get(ansi_code, None)
                if c is not None:
                    self.set_color(
                        c[0], c[1], c[2], c[3]
                    )
            elif ansi_code == _ANSI_FOREGROUND:
                c = next((
                    color['rgb'] for color in _ANSI_256_COLORS
                    if str(color['colorId']) == parameter
                ), None)
                if c is not None:
                    self.set_color(
                        _ANSI_FOREGROUND, c['r'], c['g'], c['b']
                    )
            elif ansi_code == _ANSI_BACKGROUND:
                c = next((
                    color['rgb'] for color in _ANSI_256_COLORS
                    if str(color['colorId']) == parameter
                ), None)
                if c is not None:
                    self.set_color(
                        _ANSI_BACKGROUND, c['r'], c['g'], c['b']
                    )
                pass

        def reset(self):
            self._background_color: Tuple[int] = self._background
            self._foreground_color: Tuple[int] = self._foreground
            self._intensity: int = _ANSI_INTENSITY_NORMAL
            self._style: int = _ANSI_STYLE_NORMAL
            self._underline: int = _ANSI_UNDERLINE_OFF
            self._visibility: int = _ANSI_VISIBILITY_ON
            self._negative: int = _ANSI_NEGATIVE_OFF

        def clone(self, text: str):
            ret = Ansi2Image.TextColor(text, self._foreground, self._background)
            ret._background_color = self._background_color
            ret._foreground_color = self._foreground_color
            ret._intensity = self._intensity
            ret._style = self._style
            ret._underline = self._underline
            ret._visibility = self._visibility
            ret._negative = self._negative
            return ret

        def __str__(self):
            return self.text

        def __repr__(self):
            return self.text

    def __init__(self, width, height, font_name, font_size, line_height: float = 1.0):

        self.width = width
        self.height = height
        self.font_size = font_size
        self.font_name = font_name
        self.line_height = line_height

        Ansi2Image.background_color = _BACKGROUND_COLOR
        Ansi2Image.foreground_color = _FOREGROUND_COLOR


    @classmethod
    def escape_ansi(cls, line):
        return _ANSI_SEQUENCES.sub('', line)

    @classmethod
    def _handle_ansi_code(cls, ansi: str) -> Iterator[TextColor]:
        last_end = 0  # the index of the last end of a code we've seen
        state_color = Ansi2Image.TextColor()
        for match in _ANSI_CODES_PROG.finditer(ansi):
            yield state_color.clone(ansi[last_end:match.start()])
            last_end = match.end()

            params: Union[str, List[int]]
            params, command = match.groups()

            # ESC [          = Control Sequence Introducer
            # ESC [ n m      = Select Graphic Rendition (Sets colors and style of the characters following this code)
            if command not in "m":
                continue

            while True:
                param_len = len(params)
                params = params.replace("::", ":")
                params = params.replace(";;", ";")
                if len(params) == param_len:
                    break

            try:
                params = [int(x) for x in re.split("[;:]", params)]
            except ValueError:
                params = [_ANSI_FULL_RESET]

            # Find latest reset marker
            last_null_index = None
            skip_after_index = -1
            for i, v in enumerate(params):
                if i <= skip_after_index:
                    continue

                if v == _ANSI_FULL_RESET:
                    last_null_index = i
                elif v in (_ANSI_FOREGROUND, _ANSI_BACKGROUND):
                    try:
                        x_bit_color_id = params[i + 1]
                    except IndexError:
                        x_bit_color_id = -1
                    is_256_color = x_bit_color_id == _ANSI_256_COLOR_ID
                    shift = 2 if is_256_color else 4
                    skip_after_index = i + shift

            # Process reset marker, drop everything before
            if last_null_index is not None:
                params = params[last_null_index + 1 :]

                state_color.reset()
                if not params:
                    continue

            skip_after_index = -1

            for i, v in enumerate(params):
                if i <= skip_after_index:
                    continue

                is_x_bit_color = v in (_ANSI_FOREGROUND, _ANSI_BACKGROUND)
                try:
                    x_bit_color_id = params[i + 1]
                except IndexError:
                    x_bit_color_id = -1
                is_256_color = x_bit_color_id == _ANSI_256_COLOR_ID
                is_truecolor = x_bit_color_id == _ANSI_TRUECOLOR_ID
                if is_x_bit_color and is_256_color:
                    try:
                        parameter: Optional[str] = str(params[i + 2])
                    except IndexError:
                        continue
                    skip_after_index = i + 2
                elif is_x_bit_color and is_truecolor:
                    try:
                        state_color.set_color(
                            v, params[i + 2], params[i + 3], params[i + 4]
                        )
                    except IndexError:
                        continue
                    skip_after_index = i + 4
                    continue
                else:
                    parameter = None
                state_color.adjust(v, parameter=parameter)

        yield state_color.clone(ansi[last_end:])

    def load_from_file(self, filename: str):
        with open(filename, 'rb') as f:
            self.load(io.TextIOWrapper(f))

    def load(self, stream: io.TextIOWrapper):
        self.lines = stream.readlines()

    @classmethod
    def textlength(cls, font: FreeTypeFont):
        img = Image.new("RGB", (100, 100), (0, 0, 0))
        img1 = ImageDraw.Draw(img)
        (_, _, _, h) = img1.textbbox((0, 0), text='│', font=font, spacing=0)
        (_, _, w, _) = img1.textbbox((0, 0), text='_', font=font, spacing=0)
        del img1, img
        return w, h

    def calc_size(self, width: bool = True, height: bool = True) -> None:
        max_width = max(len(self.escape_ansi(l).strip('\n ')) for l in self.lines)

        fnt = TrueTypeFont(name=self.font_name, size=self.font_size)
        (w, h) = self.textlength(fnt.truetype)

        if width:
            self.width = ((max_width * w) + self.margin * 2)
        if height:
            self.height = ((len(self.lines) * h) + self.margin * 2)

    def generate_image(self, format: str = 'png') -> bytes:

        #print(Ansi2Image.escape_ansi(''.join(self.lines)))
        #Color.p(''.join(lines), out=sys.stdout)

        img = Image.new("RGB", (self.width, self.height), self.background_color)
        img1 = ImageDraw.Draw(img)
        img1.fontmode = "RGB"

        fnt = TrueTypeFont(name=self.font_name, size=self.font_size)
        (width, height) = self.textlength(fnt.truetype)

        y = self.margin
        for line in self.lines:
            #print([m for m in Ansi2Image._handle_ansi_code(line.replace('\n', ''))])
            x = self.margin
            for c in Ansi2Image._handle_ansi_code(line.replace('\n', '')):
                img1.text((x, y), text=c.text, font=fnt.truetype, fill=c.foreground_color)
                x += width * len(c.text)
            y += int(float(height) * self.line_height)

        # Converte para bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=format, subsampling=0, quality=100)

        return img_byte_arr.getvalue()

    def save_image(self, filename: str, format: str = 'png'):
        with(open(filename, 'wb')) as f:
            f.write(self.generate_image(format=format))

def run():
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

    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        if Configuration.verbose > 0 or True:
            Color.pl('\n{!} {O}Full stack trace below')
            from traceback import format_exc
            Color.p('\n{!}    ')
            err = format_exc().strip()
            err = err.replace('\n', '\n{W}{!} {W}   ')
            err = err.replace('  File', '{W}{D}File')
            err = err.replace('  Exception: ', '{R}Exception: {O}')
            Color.pl(err)

        Color.pl('\n{!} {R}Exiting{W}\n')

    except KeyboardInterrupt:
        Color.pl('\n{!} {O}interrupted, shutting down...{W}')

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Logger.pl('{+} {C}End time {O}%s{W}' % timestamp)
    print(' ')

    sys.exit(0)
