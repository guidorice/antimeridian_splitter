from enum import Enum
import json
from typing import List, Union

from shapely import affinity
from shapely.geometry import GeometryCollection, Polygon, mapping


class OutputFormat(Enum):
    Geojson = 'geojson'
    Polygons = 'polygons'
    GeometryCollection = 'geometrycollection'


def check_crossing(lon1: float, lon2: float, validate: bool = True, dlon_threshold: float = 180.0):
    """
    Assuming a minimum travel distance between two provided longitude coordinates,
    checks if the 180th meridian (antimeridian) is crossed.
    """
    if validate and (any(abs(x) > dlon_threshold) for x in [lon1, lon2]):
        raise ValueError("longitudes must be in degrees [-180.0, 180.0]")   
    return abs(lon2 - lon1) > dlon_threshold


def translate_polygons(
    geometry_collection: GeometryCollection,
    output_format: OutputFormat = OutputFormat.Geojson
) -> Union[List[dict], List[Polygon], GeometryCollection]:

    geo_polygons = []
    for polygon in geometry_collection.geoms:
        (minx, _, maxx, _) = polygon.bounds
        if minx < -180:
            geo_polygon = affinity.translate(polygon, xoff = 360)
        elif maxx > 180:
            geo_polygon = affinity.translate(polygon, xoff = -360)
        else:
            geo_polygon = polygon

        geo_polygons.append(geo_polygon)

    if output_format == OutputFormat.Polygons:
        result = geo_polygons
    if output_format == OutputFormat.Geojson:
        result = [json.dumps(mapping(p)) for p in geo_polygons]
    elif output_format == OutputFormat.GeometryCollection:
        result = GeometryCollection(geo_polygons)

    return result
