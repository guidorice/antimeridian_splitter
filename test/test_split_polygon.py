import json

import pytest
from antimeridian_splitter import split_polygon
from shapely.geometry import geo

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
    res = split_polygon(geojson=poly, output_format='geometrycollection', validate=True)
    assert str(res) == 'GEOMETRYCOLLECTION (POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0)), POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1)))'

def test_split_polygon_to_geojson():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(geojson=poly, output_format='geojson', validate=True)
    assert len(res) == 2
    assert str(res) == """['{"type": "Polygon", "coordinates": [[[180.0, 0.0], [179.0, 0.0], [179.0, 1.0], [180.0, 1.0], [180.0, 0.0]]]}', '{"type": "Polygon", "coordinates": [[[-180.0, 1.0], [-179.0, 1.0], [-179.0, 0.0], [-180.0, 0.0], [-180.0, 1.0]]]}']"""

def test_split_polygon_to_polygons():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(geojson=poly, output_format='polygons', validate=True)
    assert len(res) == 2
    string_repr = str([str(poly) for poly in res])
    expect = """['POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0))', 'POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1))']"""
    assert expect == string_repr


# this polygon has longitude representations > 180, which this tool does not
# handle. https://github.com/guidorice/antimeridian_splitter/issues/1
invalid_polygon = """{
    "type": "Polygon",
    "coordinates": [
        [
        [
            -209.8828125,
            0.3515602939922709
        ],
        [
            -129.7265625,
            0.3515602939922709
        ],
        [
            -129.7265625,
            48.922499263758255
        ],
        [
            -209.8828125,
            48.922499263758255
        ],
        [
            -209.8828125,
            0.3515602939922709
        ]
        ]
    ]
    }
"""

def test_lng_greater_than_180():
    poly: dict = json.loads(invalid_polygon)
    with pytest.raises(ValueError):
        split_polygon(geojson=poly, output_format='geojson', validate=True)

