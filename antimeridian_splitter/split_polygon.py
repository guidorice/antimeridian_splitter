import copy
from functools import reduce
import math
from typing import List, Union
from enum import Enum
import sys

from shapely.geometry import GeometryCollection, LineString, Polygon
from shapely.ops import split

# https://gist.github.com/PawaritL/ec7136c0b718ca65db6df1c33fd1bb11
from .geopolygon_utils import check_crossing, translate_polygons, OutputFormat


class AcceptedGeojsonTypes(Enum):
    Polygon = 'Polygon'
    MultiPolygon = 'MultiPolygon'


def split_coords(src_coords: List[List[List[float]]]) -> GeometryCollection:
    coords_shift = copy.deepcopy(src_coords)
    shell_minx = sys.float_info.max
    shell_maxx = sys.float_info.min

    # it is possible that the shape provided may be defined as more than 360
    #   degrees in either direction. Under these circumstances the shifted polygon
    #   would cross both the 180 and the -180 degree representation of the same
    #   meridian. This is not allowed, but checked for using the len(split_meriditans)
    split_meridians = set()

    for ring_index, ring in enumerate(coords_shift):
        if len(ring) < 1: 
            continue
        else:
            ring_minx = ring_maxx = ring[0][0]
            crossings = 0

        for coord_index, (lon, _) in enumerate(ring[1:], start=1):
            lon_prev = ring[coord_index - 1][0] # [0] corresponds to longitude coordinate
            if check_crossing(lon, lon_prev, validate=False):
                direction = math.copysign(1, lon - lon_prev)
                coords_shift[ring_index][coord_index][0] = lon - (direction * 360.0)
                crossings += 1

            x_shift = coords_shift[ring_index][coord_index][0]
            if x_shift < ring_minx: ring_minx = x_shift
            if x_shift > ring_maxx: ring_maxx = x_shift

        # Ensure that any holes remain contained within the (translated) outer shell
        if (ring_index == 0): # by GeoJSON definition, first ring is the outer shell
            shell_minx, shell_maxx = (ring_minx, ring_maxx)
        elif (ring_minx < shell_minx):
            ring_shift = [[x + 360, y] for (x, y) in coords_shift[ring_index]]
            coords_shift[ring_index] = ring_shift
            ring_minx, ring_maxx = (x + 360 for x in (ring_minx, ring_maxx))
        elif (ring_maxx > shell_maxx):
            ring_shift = [[x - 360, y] for (x, y) in coords_shift[ring_index]]
            coords_shift[ring_index] = ring_shift
            ring_minx, ring_maxx = (x - 360 for x in (ring_minx, ring_maxx))

        if crossings: # keep track of meridians to split on
            if ring_minx < -180: split_meridians.add(-180)
            if ring_maxx > 180: split_meridians.add(180)

    n_splits = len(split_meridians)
    if n_splits == 0:
        shell, *holes = src_coords
        split_polygons = GeometryCollection([Polygon(shell, holes)])
    elif n_splits == 1:
        split_lon = split_meridians.pop()
        meridian = [[split_lon, -90.0], [split_lon, 90.0]]
        splitter = LineString(meridian)

        shell, *holes = coords_shift
        split_polygons = split(Polygon(shell, holes), splitter)
    else:
        raise NotImplementedError(
            """Splitting a Polygon by multiple meridians (MultiLineString) 
               not supported by Shapely"""
        )
    return split_polygons


def split_polygon(geojson: dict, output_format: OutputFormat = OutputFormat.Geojson) -> Union[
    List[dict], List[Polygon], GeometryCollection
]:
    """
    Given a GeoJSON representation of a Polygon, returns a collection of
    'antimeridian-safe' constituent polygons split at the 180th meridian, 
    ensuring compliance with GeoJSON standards (https://tools.ietf.org/html/rfc7946#section-3.1.9)

    Assumptions:
      - Any two consecutive points with over 180 degrees difference in
        longitude are assumed to cross the antimeridian
      - The polygon spans less than 360 degrees in longitude (i.e. does not wrap around the globe)
      - However, the polygon may cross the antimeridian on multiple occasions

    Parameters:
        geojson (dict): GeoJSON of input polygon to be split. For example:
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [179.0, 0.0], [-179.0, 0.0], [-179.0, 1.0],
                            [179.0, 1.0], [179.0, 0.0]
                        ]
                    ]
                }
        output_format (str): Available options: "geojson", "polygons", "geometrycollection"
                             If "geometrycollection" returns a Shapely GeometryCollection.
                             Otherwise, returns a list of either GeoJSONs or Shapely Polygons

    Returns:
        List[dict]/List[Polygon]/GeometryCollection: antimeridian-safe polygon(s)
    """
    geotype = AcceptedGeojsonTypes(geojson['type'])
    if geotype is AcceptedGeojsonTypes.Polygon:
        split_polygons = split_coords(geojson['coordinates'])
    elif geotype is AcceptedGeojsonTypes.MultiPolygon:
        split_polygons = reduce(
            GeometryCollection.union,
            (split_coords(coords) for coords in geojson['coordinates'])
        )
    return translate_polygons(split_polygons, output_format)
