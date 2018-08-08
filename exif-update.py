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
import dateutil.parser
import datetime
import fractions

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

set_location = None

if options.location:
    geo = parse_geo(options.location)
    if geo:
        set_location = geo
    else:
        for l in configuration["locations"]:
            if l.get("name") == options.location:
                break
        else:
            help("location '%s' not found in database" % options.location)

        geo = l.get("geo")
        if not geo:
            help("location '%s in database didn't have 'geo'" % options.location)

        geo = parse_geo(geo)
        if not geo:
            help("location '%s in database didn't have valid 'geo'" % options.location)

        set_location = geo

## parse the date
set_date = None

if options.date:
    dt = dateutil.parser.parse(options.date)
    if not dt:
        help("date '%s could not be parsed" % options.date)

    set_date = dt.strftime("%Y:%m:%d %H:%M:%S")

if not set_location and not set_date:
    help("at least one of --date or --location are required")

## this code from https://gist.github.com/c060604/8a51f8999be12fc2be498e9ca56adc72
def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = fractions.Fraction(str(number))
    return (f.numerator, f.denominator)

def cook_photo(photo):
    exif = piexif.load(photo)

    if set_date:
        d = exif.setdefault("Exif", {})

        d[piexif.ExifIFD.DateTimeOriginal] = set_date

    if set_location:
        lat_deg = to_deg(set_location[0], [ "S", "N" ])
        lng_deg = to_deg(set_location[1], [ "W", "E" ])

        exiv_lat = (
            change_to_rational(lat_deg[0]), 
            change_to_rational(lat_deg[1]), 
            change_to_rational(lat_deg[2])
        )
        exiv_lng = (
            change_to_rational(lng_deg[0]), 
            change_to_rational(lng_deg[1]), 
            change_to_rational(lng_deg[2])
        )

        d = exif.setdefault("GPS", {})

        d[piexif.GPSIFD.GPSVersionID] = ( 2, 0, 0, 0 )
        d[piexif.GPSIFD.GPSLatitudeRef] = lat_deg[3]
        d[piexif.GPSIFD.GPSLatitude] = exiv_lat
        d[piexif.GPSIFD.GPSLongitudeRef] = lng_deg[3]
        d[piexif.GPSIFD.GPSLongitude] = exiv_lng

    print photo
    bytes = piexif.dump(exif)
    piexif.insert(bytes, photo)

## do the main work
for photo in args:
    if os.path.isdir(photo):
        subs = os.listdir(photo)
        for sub in subs:
            if os.path.splitext(sub)[1].lower() not in [ ".jpg" ]:
                continue

            cook_photo(os.path.join(photo, sub))
    else:
        cook_photo(photo)
