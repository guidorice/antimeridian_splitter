from .split_polygon import split_polygon
from .geopolygon_utils import OutputFormat
import json
from functools import reduce
from shapely.geometry.base import BaseGeometry
import shapely.geometry

example_polygon1 = """
{
    "type": "Polygon",
    "coordinates": [
        [
        [179.0, 0.0], [-179.0, 0.0], [-179.0, 1.0],
        [179.0, 1.0], [179.0, 0.0]
        ]
    ]
}"""

def test_split_polygon_to_geometrycollection():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(poly, OutputFormat.GeometryCollection)
    assert str(res) == 'GEOMETRYCOLLECTION (POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0)), POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1)))'

def test_split_polygon_to_geojson():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(poly, OutputFormat.Geojson)
    assert str(res) == """['{"type": "Polygon", "coordinates": [[[180.0, 0.0], [179.0, 0.0], [179.0, 1.0], [180.0, 1.0], [180.0, 0.0]]]}', '{"type": "Polygon", "coordinates": [[[-180.0, 1.0], [-179.0, 1.0], [-179.0, 0.0], [-180.0, 0.0], [-180.0, 1.0]]]}']"""
    assert len(res) == 2

def test_split_polygon_to_polygons():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(poly, OutputFormat.GeometryCollection)
    assert len(res) == 2
    string_repr = str([str(poly) for poly in res])
    expect = """['POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0))', 'POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1))']"""
    assert expect == string_repr


example_multipolygon = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                [179.0, 55.0],
                [179.0, 56.0],
                [179.0, 56.0],
                [179.0, 57.0],
                [179.0, 57.0],
                [180.0, 58.0],
                [180.0, 55.0],
                [179.0, 55.0]
            ],
        ],
        [
            [
                [-180.0, 58.0],
                [-179.0, 58.0],
                [-175.0, 57.0],
                [-175.0, 57.0],
                [-175.0, 56.0],
                [-176.0, 56.0],
                [-176.0, 55.0],
                [-176.0, 55.0],
                [-180.0, 55.0],
                [-180.0, 58.0]
            ],
        ]
    ]
}

def test_split_multipolygons():
    polygon_collection = split_polygon(example_multipolygon, OutputFormat.Polygons)
    target_multipolygon = reduce(BaseGeometry.union, polygon_collection)
    assert json.dumps(example_multipolygon) == json.dumps(shapely.geometry.mapping(target_multipolygon))

