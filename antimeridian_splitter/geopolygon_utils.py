import json
from typing import Generator, List, Union

from shapely import affinity
from shapely.geometry import GeometryCollection, Polygon, mapping


def check_crossing(lon1: float, lon2: float, validate: bool = False, dlon_threshold: float = 180.0):
    """
    Assuming a minimum travel distance between two provided longitude coordinates,
    checks if the 180th meridian (antimeridian) is crossed.
    """
    print(f'check_crossing for lon1: {lon1} lon2: {lon2}')
    if validate and any (abs(x) > 180.0 for x in [lon1, lon2]):
        raise ValueError("longitudes must be in degrees [-180.0, 180.0]")   
    return abs(lon2 - lon1) > dlon_threshold

def translate_polygons(geometry_collection: GeometryCollection, 
                       output_format: str = "geojson") -> Generator[
                          Union[List[dict], List[Polygon]], None, None
                       ]:
    
  for polygon in geometry_collection:
      (minx, _, maxx, _) = polygon.bounds
      if minx < -180: geo_polygon = affinity.translate(polygon, xoff = 360)
      elif maxx > 180: geo_polygon = affinity.translate(polygon, xoff = -360)
      else: geo_polygon = polygon

      yield_geojson = output_format == "geojson"
      yield json.dumps(mapping(geo_polygon)) if (yield_geojson) else geo_polygon
