#
#   exif-update.py
#
#   David Janes
#   2018-08-06
#

import sys
import path
import os
import optparse
import yaml
import piexif

## define arguments
parser = optparse.OptionParser()
parser.add_option(
    "", "--debug",
    default = False,
    action = "store_true",
    dest = "debug",
    help = "",
)
parser.add_option(
    "", "--location",
    dest = "location",
    help = "location to add to photos (lat,lon OR name of place)",
)
parser.add_option(
    "", "--date",
    dest = "date",
    help = "set the creation date of the phot"
)

## parse
(options, args) = parser.parse_args()

class OptionException(Exception):
    pass

try:
    if not args:
        raise   OptionException, "at least one filename required"
except OptionException, s:
    print >> sys.stderr, "%s: %s\n" % ( sys.argv[0], s, )
    parser.print_help(sys.stderr)
    sys.exit(1)

## load configuration
