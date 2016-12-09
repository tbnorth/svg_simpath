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

def flint(x):
    return int(float(x))

def coord_split(s):
    return map(flint, s.split(','))

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
                del points[-1]
            closed = points[-1] == 'z'
            if closed:
                del points[-1]
            if len(points) > 50:
                sys.stderr.write("%s ->" % (len(points)/2))
                # points = reduce(operator.add, 
                #     [points[i:i+2] for i in range(0,len(points),10)])
                
                new_points = points[:2]
                coord = coord_split(points[1])
                for idx in range(2, len(points), 2):
                    try:
                        new_coord = coord_split(points[idx+1])
                    except:
                        sys.stderr.write("%s\n" % d[:50])
                        sys.stderr.write("%s\n" % d[-50:])
                        sys.stderr.write("%s\n" % points[:8])
                        sys.stderr.write("%s\n" % points[-8:])
                        raise
                    if new_coord != coord:
                        coord = new_coord
                        new_points.extend(points[idx:idx+2])
                
                sys.stderr.write("%s\n" % (len(new_points)/2))
                if closed:
                    new_points.append('z')
                attrs = dict(attrs)
                attrs['d'] = ''.join(new_points)
        return XMLFilterBase.startElement(self, name, AttributesImpl(attrs))

def main():
    parser = sax.make_parser()
    downstream_handler = XMLGenerator(sys.stdout)
    filter_handler = PathSimplify(parser)
    filter_handler.setContentHandler(downstream_handler)
    filter_handler.parse(sys.argv[1])

if __name__ == '__main__':
    main()
