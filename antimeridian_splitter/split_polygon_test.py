from .spit_polygon import split_polygon
import json

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
    res = split_polygon(poly, 'geometrycollection')
    assert str(res) == 'GEOMETRYCOLLECTION (POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0)), POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1)))'

def test_split_polygon_to_geojson():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(poly, 'geojson')
    assert len(res) == 2
    assert str(res) == """['{"type": "Polygon", "coordinates": [[[180.0, 0.0], [179.0, 0.0], [179.0, 1.0], [180.0, 1.0], [180.0, 0.0]]]}', '{"type": "Polygon", "coordinates": [[[-180.0, 1.0], [-179.0, 1.0], [-179.0, 0.0], [-180.0, 0.0], [-180.0, 1.0]]]}']"""

def test_split_polygon_to_polygons():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(poly, 'polygons')
    assert len(res) == 2
    string_repr = str([str(poly) for poly in res])
    expect = """['POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0))', 'POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1))']"""
    assert expect == string_repr


