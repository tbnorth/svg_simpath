"""
svg_simpath.py - simplify paths in SVG files
Terry N. Brown, terrynbrown@gmail.com, Fri Dec 09 12:45:02 2016
"""

import argparse
import operator
import os
import re
import sys
from collections import namedtuple, defaultdict

from xml import sax
from xml.sax.saxutils import XMLGenerator
from xml.sax.saxutils import XMLFilterBase
from xml.sax.xmlreader import AttributesImpl

PATHSPLIT = re.compile(r'([MLz])')
WHITESPACE = re.compile(r'[ \t\n]')

def make_parser():
    """build an argparse.ArgumentParser, don't call this directly,
       call get_options() instead.
    """
    parser = argparse.ArgumentParser(
        description="""Simplify SVG path elements""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--res", default='1',
        help="snapping resolution"
    )

    return parser


def get_options(args=None):
    """
    get_options - use argparse to parse args, and return a
    argparse.Namespace, possibly with some changes / expansions /
    validatations.

    Client code should call this method with args as per sys.argv[1:],
    rather than calling make_parser() directly.

    :param [str] args: arguments to parse
    :return: options with modifications / validations
    :rtype: argparse.Namespace
    """
    opt = make_parser().parse_args(args)

    # modifications / validations go here

    return opt


class PathSimplify(XMLFilterBase):

    def __init__(self, res):    
        XMLFilterBase.__init__(self, sax.make_parser())
        try:
            res = int(res)
        except ValueError:
            res = float(res)
        self.res = res
        if isinstance(self.res, int):
            self.round = self.round_int
        else:
            self.round = self.round_float

    def round_float(self, x):
        return int(float(x))
    def round_int(self, x):
        return int(float(x))
    
    def coord_split(self, s):
        return map(self.round, s.split(','))
    
    def startElement(self, name, attrs):
        if name == 'path':
            d = attrs.get('d', [])
            if not d:
                return XMLFilterBase.startElement(self, name, attrs)
                
            subpaths = d.split('z')
            full_path = []
            
            for d_n, d in enumerate(subpaths):
                if not d:
                    continue
                closed = d_n+1 < len(subpaths)
                
                points = PATHSPLIT.split(WHITESPACE.sub('', d))
                assert not points[0], points[0]
                del points[0]
        
                if len(points) > 50:
                    sys.stderr.write("%s ->" % (len(points)/2))
                    # points = reduce(operator.add, 
                    #     [points[i:i+2] for i in range(0,len(points),10)])
                    
                    new_points = points[:2]
                    coord = self.coord_split(points[1])
                    for idx in range(2, len(points), 2):
                        new_coord = self.coord_split(points[idx+1])
                        if new_coord != coord or idx+2 == len(points):
                            coord = new_coord
                            new_points.extend(points[idx:idx+2])
                                                
                    sys.stderr.write("%s\n" % (len(new_points)/2))
                    
                else:
                    new_points = points
                    
                if closed:
                    new_points.append('z')
                    
                full_path.append(''.join(new_points))

            attrs = dict(attrs)
            attrs['d'] = ''.join('\n'.join(full_path))

        return XMLFilterBase.startElement(self, name, AttributesImpl(attrs))

def main():
    opt = get_options()
    downstream_handler = XMLGenerator(sys.stdout)
    filter_handler = PathSimplify(opt.res)
    filter_handler.setContentHandler(downstream_handler)
    filter_handler.parse(sys.stdin)

if __name__ == '__main__':
    main()
