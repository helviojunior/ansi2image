# ANSI to Image

A Python lib to convert ANSI text to Image

[![Build](https://github.com/helviojunior/ansi2image/actions/workflows/build_and_publish.yml/badge.svg)](https://github.com/helviojunior/ansi2image/actions/workflows/build_and_publish.yml)
[![Build](https://github.com/helviojunior/ansi2image/actions/workflows/build_and_test.yml/badge.svg)](https://github.com/helviojunior/ansi2image/actions/workflows/build_and_test.yml)
[![Downloads](https://pepy.tech/badge/ansi2image/month)](https://pepy.tech/project/ansi2image)
[![Supported Versions](https://img.shields.io/pypi/pyversions/ansi2image.svg)](https://pypi.org/project/ansi2image)
[![Contributors](https://img.shields.io/github/contributors/helviojunior/ansi2image.svg)](https://github.com/helviojunior/ansi2image/graphs/contributors)
[![PyPI version](https://img.shields.io/pypi/v/ansi2image.svg)](https://pypi.org/project/ansi2image/)
[![License: GPL-3.0](https://img.shields.io/pypi/l/ansi2image.svg)](https://github.com/helviojunior/ansi2image/blob/main/LICENSE)

ANSI2Image officially supports Python 3.8+.

## Main features

* [x] Read ANSI file (or ANSI stdin) and save an image (JPG or PNG)

## Installation

```bash
pip3 install --upgrade ansi2image
```

## Help

```bash
ANSI to image v0.1.1 by Helvio Junior
ANSI to Image convert ANSI text to an image.
https://github.com/helviojunior/ansi2image
    
positional arguments:
  [filename]             File path or - to stdin

Options:
  -o--output [filename]  image output file.
  --font [font]          font type. (default: JetBrains Mono Regular).
  --font-list            List all supported font family and variations
  -h, --help             show help message and exit
  -v                     Specify verbosity level (default: 0). Example: -v, -vv, -vvv
  --version              show current version

```

## ANSI reference

https://en.wikipedia.org/wiki/_ANSI_escape_code