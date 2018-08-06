#
#   exif-update.py
#
#   David Janes
#   2018-08-06
#

import sys
import os
import pprint
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

def help(message):
    if message:
        print >> sys.stderr, "%s: %s\n" % ( sys.argv[0], message, )
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        parser.print_help(sys.stdout)
        sys.exit(0)

try:
    if not args:
        raise   OptionException, "at least one filename required"
except OptionException, s:
    print >> sys.stderr, "%s: %s\n" % ( sys.argv[0], s, )
    parser.print_help(sys.stderr)
    sys.exit(1)

## load configuration
configuration = {
    "locations": []
}

for p in [ ".exif-update.yaml", os.path.expanduser("~/.exif-update.yaml"), ]:
    try:
        data = yaml.load(file(p))
    except IOError:
        continue

    for key, value in data.items():
        if not configuration.get(key):
            configuration[key] = value
        elif isinstance(value, dict) and isinstance(configuration[key], dict):
            configuration[key] = configuration[key].update(value)
        elif isinstance(value, list) and isinstance(configuration[key], dict):
            configuration[key] = configuration[key].extend(value)
        else:
            configuration[key] = value

## narrow down the location
def parse_geo(v):
    if not v:
        return

    parts = v.split(",")
    if len(parts) != 2:
        return 

    try:
        return map(float, parts)
    except:
        return

location = None

if options.location:
    geo = parse_geo(options.location)
    if geo:
        location = geo
    else:
        for l in configuration["locations"]:
            if l.get("name") == options.location:
                break
        else:
            l = None

        if not l:
            help("location '%s' not found in database" % options.location)

        geo = l.get("geo")
        if not geo:
            help("location '%s in database didn't have 'geo'" % options.location)

        geo = parse_geo(geo)
        if not geo:
            help("location '%s in database didn't have valid 'geo'" % options.location)

        location = geo

print location
"""
ls = configuration["locations"]
ls = filter(lambda l: l.get("name"), ls)
ls = dict(zip(map(lambda l: l.get("name"), ls), ls))
configuration["locations"] = ls

pprint.pprint(configuration)
"""
