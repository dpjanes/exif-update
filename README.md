# exif-update
CLI update EXIF info on images

This was written because I had a bunch of images that
had incorrect datestamps and no lat/long information.

Basic usage is like:

    python exif-update.py \
        --date "1:32pm Jan 1, 1991" \
        --location glasgow \
        SAMPLE.jpg

## Libraries

Make sure the following are installed:

* [dateutil](https://dateutil.readthedocs.io/en/stable/)
* [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
* [piexif](http://piexif.readthedocs.io/en/latest/index.html)

## See Also

* [LatLong.net](https://www.latlong.net/) - good for looking update Lat,Lon
