# Copyright © 2022 Eric Diven

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details. */

import argparse
import sys

from svgwrite import drawing
from svgwrite import inch
from svgwrite import mm

# because we're fucking barbarians here...
UNIT = inch
WIDTH = 17
HEIGHT = 11
MARGIN = .75
ROW_HEIGHT = .25
TEXT_HEIGHT = 0.188

STYLESHEET = "style.css"

PAPERS = {
        'ledger': (17, 11, inch),
        'a3': (420, 297, mm)
        }

# global layout debug flag
DEBUG = False

'''
Handles most of the title block rows that can be customized with a command line argument. Parent class for the remaining weird ones.
'''
class TitleRow:

    def __init__(self, arg, default, fudge, fmt):
        self.arg = arg
        self.default = default
        self.fudge = fudge
        self.fmt = fmt

    def add_argument(self, parser):
        parser.add_argument(self.arg, default=self.default, action="store")

    def key_of(self):
        return self.arg.lstrip("-").replace("-", "_")

    def label_of(self):
        return self.arg.lstrip("-").replace("-", " ").upper() + ":"

    def content(self, args):
        fmt_arg = args.get(self.key_of())
        return self.fmt.format(fmt_arg)

    def add_line(self, lines, args):
        lines.append((self.fudge, self.label_of(), self.content(args)))

'''
Handles "DRAWING:   # OF #" in the title block.
no --drawing arg leaves blanks to be filled in by hand
--drawing 2 results in "DRAWING:   2 OF 2"
--drawing 2,3 results in "DRAWING:   2 OF 3"
'''
class DrawingTitleRow(TitleRow):

    def __init__(self, arg, default, fudge, fmt):
        super().__init__(arg, default, fudge, fmt)

    @staticmethod
    def validate(arg):
        args = arg.split(",")

        if len(args) == 1:
            return [args[0], args[0]]
        elif len(args) == 2:
            return args
        else:
            raise argparse.ArgumentTypeError(
                    "argument to {} must be of the format # or #,#")

    def add_argument(self, parser):
        parser.add_argument(self.arg, default=self.default,
                action="store", type=self.validate)

    def content(self, args):
        [d, of] = args.get(self.key_of())
        return self.fmt.format(d, of)

'''
Handles title block information that can have multiple rows. Currently: address
Multiple --address arguments will result in something like

ADDRESS:   first-address-arg-value
           second-address-arg-value
           third-address-arg-value
'''
class TitleMultiRow(TitleRow):

    def __init__(self, arg, default, fudge, fmt):
        super().__init__(arg, None, fudge, fmt)
        self.default = default

    def add_argument(self, parser):
        parser.add_argument(self.arg, default=None,
                action="append")

    def add_line(self, lines, args):
        rows = args.get(self.key_of())
        if rows is None:
            rows = self.default
        for i, row in enumerate(rows):
            if i == 0:
                lines.append((self.fudge, self.label_of(), row))
            else:
                lines.append((0, "", row))

'''
Rows relative to the direction of the text. Deal; that's not the worst thing
happening here. Read on

The whole point of this is to ultimately cough up a tuple of the following
schema when we got to format the title block:

(fudge, label, content)

The first element in the tuple fudges the label over because I can't be
bothered to figure out how to right align the label. This is in inches, so if
you change the text height, all bets are off. Changing the font will likewise
cause havoc.

The leading whitespace in "OF" needs to be preserved in the styling.
Fortunately, that can be safely applied to all of the content.
'''
TITLE_ROWS = [
        TitleRow("--project", "", .14, "{}"),
        TitleRow("--drawn-by", "", 0, "{}"),
        TitleMultiRow("--address", ["", ""], .085, "{}"),
        TitleRow("--phone", "", .33, "{}"),
        TitleRow("--email", "", .43, "{}"),
        DrawingTitleRow("--drawing", "", .090, "                {} OF {}")]

TITLE_ROW_WIDTH = 5.5
TITLE_LABEL_OFFSET = .25
TITLE_CONTENT_OFFSET = 1.5

'''
schema: (
    offset from previous vertical line,
    column title,
    vertical line y adjust,
    [(superheader title, x fudge)])

If offset from previous vertical line is postive, it ultimately references the
left border of the main block. If it's negative, it ultimately references the
right boarder. This is meant to let some column other than the right-most one
absorb any squish from an arbitrary number of address lines.

If you have more than one column that's right-referenced, you'll want to list
them in reverse order in the list below. That's not very ergonomic, but such is
life. Submit a PR if it bugs you.

Important caveat: All the y_adjusts will need to be the same for this to look
right.
'''
MAIN_COLUMNS = [
        (0, "PART", 0, None),
        (2.5, "#", -ROW_HEIGHT, None),
        (.5, "L", 0, ("ROUGH", 0)),
        (.5, "W", 0, None),
        (.5, "T", 0, None),
        (.5, "", -ROW_HEIGHT, None),
        (1/16, "#", -ROW_HEIGHT, None),
        (.5, "L", 0, ("FINISHED", -1/8)),
        (.5, "W", 0, None),
        (.5, "T", 0, None),
        (.5, "WOOD", -ROW_HEIGHT, None),
        (1.5, "COMMENTS", 0, None),
        (-1.25, "BOARD FT", 0, None),
        ]

def title_block(d, rows):
    x0 = WIDTH - MARGIN
    x = WIDTH - MARGIN
    y1 = (HEIGHT - TITLE_ROW_WIDTH) / 2
    y2 = y1 + TITLE_ROW_WIDTH

    for row in reversed(rows):
        (fudge, label, content) = row
        d.add(d.line(
            (x * UNIT, y1 * UNIT),
            (x * UNIT, y2 * UNIT),
            **{"class": "l"}))
        x -= ROW_HEIGHT

        '''
        What a pain in the nuts this is.

        The rotate transform rotates an element about the origin of the
        document, not about any particular part of the element. Convenient,
        that.

        Applying `transform: rotate(-90deg)' places the label somewhere off the
        boundary of the page. This can be done via some matrix multiplication
        to the full list of points that define the figure.

        Putting the text back where we want it can be done via (basically)
        rotating it back into place via changing the x and y coordinates of the
        text appropriately. Because we're "rotating" only the insertion point
        of the text, the text itself remains vertical.

        That could *also* be done via matrix multiplication, but that seemed
        like a lot of hassle for just swapping x and y and multiplying one of
        them by -1 in what needs to be a tuple anyway.
        '''
        d.add(d.text(
            label,
            ((-y2 + TITLE_LABEL_OFFSET + fudge) * UNIT, (x + TEXT_HEIGHT) * UNIT),
            **{"class": "title-label"}))

        d.add(d.text(
            content,
            ((-y2 + TITLE_CONTENT_OFFSET) * UNIT, (x + TEXT_HEIGHT) * UNIT),
            **{"class": "title-content"}))

    # left-most vertical line
    d.add(d.line((x * UNIT, y1 * UNIT), (x * UNIT, y2 * UNIT),
            **{"class": "l"}))

    # top line
    d.add(d.line((x0 * UNIT, y1 * UNIT), (x * UNIT, y1 * UNIT),
            **{"class": "l"}))

    #bottom line
    d.add(d.line((x0 * UNIT, y2 * UNIT), (x * UNIT, y2 * UNIT),
            **{"class": "l"}))

    if DEBUG:
        d.add(d.line(
            (x0 * UNIT, (y2 - 1.25) * UNIT),
            (x * UNIT, (y2 - 1.25) * UNIT),
            **{"class": "debug"}))

    return x

def main_block(d, max_x):

    x1 = MARGIN
    x2 = max_x
    y = MARGIN + ROW_HEIGHT

    # row divider lines
    while (y <= HEIGHT - MARGIN):
        d.add(d.line(
            (x1 * UNIT, y * UNIT),
            (x2 * UNIT, y * UNIT),
            **{"class": "l"}))

        y += ROW_HEIGHT

    # column divider lines and titles
    lx = MARGIN
    rx = max_x
    y1 = MARGIN + ROW_HEIGHT
    y2 = y - ROW_HEIGHT
    rf_last = 0
    rf_x1 = None
    for (offset, title, y_adjust, superheader) in MAIN_COLUMNS:

        if (offset < 0):
            rx += offset
            x = rx
        else:
            lx += offset
            x = lx

        text_x = x + 3/16
        d.add(d.line(
            (x * UNIT, (y1 + y_adjust) * UNIT),
            (x * UNIT, y2 * UNIT),
            **{"class": "l"}))

        d.add(d.text(
            title,
            ((text_x) * UNIT, (y1 + TEXT_HEIGHT) * UNIT),
            **{"class": "label"}))

        '''
        Find the leftmost and rightmost superheader block x coordinates.
        rf here meaning Rough/Finished.

        This will only look right if all the y_adjusts are the same.
        '''
        if (y_adjust != 0):
            rf_last_x = x
            if rf_x1 is None:
                rf_x1 = rf_last_x

        if superheader is None:
            continue

        # Add the superheader text if we have it.
        (title, fudge) = superheader
        d.add(d.text(
            title,
            ((text_x + fudge) * UNIT, (y1 - ROW_HEIGHT + TEXT_HEIGHT) * UNIT),
            **{"class": "label"}))

    # rightmost vertical line of the main block
    d.add(d.line(
        (max_x * UNIT, y1 * UNIT),
        (max_x * UNIT, y2 * UNIT),
        **{"class": "l"}))

    # Add the top line for the superheader block
    d.add(d.line(
        (rf_x1 * UNIT, MARGIN * UNIT),
        (rf_last_x * UNIT, MARGIN * UNIT),
        **{"class": "l"}))


def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--paper", action="store", default="ledger",
            choices=PAPERS.keys())
    parser.add_argument('--link-style', action='store_true')
    parser.add_argument('filename', nargs='?')

    for title_row in TITLE_ROWS:
        title_row.add_argument(parser)

    args = parser.parse_args()

    title_rows = []
    for title_row in TITLE_ROWS:
        title_row.add_line(title_rows, vars(args))

    link_style = args.link_style
    filename = args.filename

    global DEBUG
    DEBUG = args.debug

    (paper_width, paper_height, paper_unit) = PAPERS[args.paper]

    d = drawing.Drawing("cutlist.svg", (paper_width * paper_unit,
        paper_height * paper_unit))

    # External stylesheet support is sort of iffy. Browsers seem to be OK with
    # it, CorelDraw seems to be OK with it, other renderers not so much.
    if link_style:
        d.add_stylesheet(STYLESHEET, "asdf")
    else:
        with open(STYLESHEET, 'r') as style:
            d.embed_stylesheet(style.read())

    global WIDTH
    global HEIGHT

    if (paper_unit == mm):
        WIDTH = paper_width / 25.4
        HEIGHT = paper_height / 25.4
    elif (paper_unit == inch):
        WIDTH = paper_width
        HEIGHT = paper_height
    else:
        raise Exception("Unknown paper unit")

    if DEBUG:
        d.add(d.rect(
            (0 * UNIT, 0 * UNIT),
            (WIDTH * UNIT, HEIGHT * UNIT),
            **{"class": "debug"}))

    title_min_x = title_block(d, title_rows)
    main_max_x = title_min_x - MARGIN

    main_block(d, main_max_x)

    if filename is not None:
        with open(filename, 'w', encoding='utf-8') as output:
            d.write(output, pretty=True)
    else:
        d.write(sys.stdout, pretty=True)

if __name__ == "__main__":
    main()
