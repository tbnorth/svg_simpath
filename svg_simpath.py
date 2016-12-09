"""
svg_simpath.py - simplify paths in SVG files
Terry N. Brown, terrynbrown@gmail.com, Fri Dec 09 12:45:02 2016
"""

import operator
import os
import re
import sys
from collections import namedtuple, defaultdict

import sys
from xml import sax
from xml.sax.saxutils import XMLGenerator

from xml.sax.saxutils import XMLFilterBase

from xml.sax.xmlreader import AttributesImpl

PATHSPLIT = re.compile(r'([MLz])')
WHITESPACE = re.compile(r'[ \t\n]')

class PathSimplify(XMLFilterBase):

    def startElement(self, name, attrs):
        if name == 'path':
            d = attrs.get('d', [])
            if not d:
                return XMLFilterBase.startElement(self, name, attrs)
            points = PATHSPLIT.split(WHITESPACE.sub('', d))
            assert not points[0], points[0]
            del points[0]
            if not points[-1]:
                del points[1]
            closed = points[-1] == 'z'
            if closed:
                del points[-1]
            if len(points) > 50:
                sys.stderr.write("%s\n" % len(points))
                points = reduce(operator.add, 
                    [points[i:i+2] for i in range(0,len(points),10)])
                if closed:
                    points.append('z')
                attrs = dict(attrs)
                attrs['d'] = ''.join(points)
        return XMLFilterBase.startElement(self, name, AttributesImpl(attrs))

def main():
    parser = sax.make_parser()
    downstream_handler = XMLGenerator(sys.stdout)
    filter_handler = PathSimplify(parser)
    filter_handler.setContentHandler(downstream_handler)
    filter_handler.parse(sys.argv[1])

if __name__ == '__main__':
    main()
