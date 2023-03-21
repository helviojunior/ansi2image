import os
from pathlib import Path
from typing import Optional

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont


class TrueTypeFont(object):
    _fonts = []
    _ttf = None
    _name = ''

    def __init__(self, name: str = 'JetBrains Mono Regular', size: int = 12):
        self.fonts = TrueTypeFont.load_fonts()
        self._name = name
        self.ttf = TrueTypeFont.get_font_by_name(self.name, size)

        if self.ttf is None:
            raise Exception(f'Font with name "{self.name}" not found!')

    @property
    def name(self):
        return self._name

    @property
    def truetype(self):
        return self.ttf

    @staticmethod
    def _font_data(path: str):
        variation = []
        name = ''
        for i in range(20):
            try:
                ttf = ImageFont.truetype(path, 10, index=i)
                name = ttf.getname()[0]
                variation.append(dict(index=i, name=' '.join(ttf.getname())))
            except:
                break

        return dict(
            path=path,
            name=name,
            variation=variation
        )

    @staticmethod
    def load_fonts() -> list:
        if TrueTypeFont._fonts is not None and len(TrueTypeFont._fonts) > 0:
            return TrueTypeFont._fonts

        font_path = os.path.join(Path(os.path.dirname(__file__)).resolve().parent, 'fonts')
        TrueTypeFont._fonts = [
            font for name in os.listdir(font_path)
            if os.path.isfile(os.path.join(font_path, name)) and \
               (font := TrueTypeFont._font_data(os.path.join(font_path, name)))
        ]
        return TrueTypeFont._fonts

    @staticmethod
    def get_font_by_name(name: str, size: int = 12) -> Optional[FreeTypeFont]:
        return next((
            ImageFont.truetype(str(fnt['path']), size, index=v['index'])
            for fnt in TrueTypeFont._fonts for v in fnt['variation']
            if v['name'].lower() == name.lower() or f'{name.lower()} regular' == v['name'].lower()
        ), None)
