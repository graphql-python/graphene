from __future__ import absolute_import
from collections import Iterable

from graphql.language import ast

from .scalars import Scalar

try:
    import shapely
    from shapely import geometry
    from shapely.wkt import loads
except:
    raise ImportError(
        "shapely package is required for Graphene geo.\n"
        "You can install it using: pip install shapely."
    )


def get_coords(geom):
    if isinstance(geom, Iterable):
        return geom
    return geom.coords


class Point(Scalar):
    '''
    The `Point` scalar type represents a Point
    value as specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    '''

    @staticmethod
    def serialize(point):
        coords = get_coords(point)
        assert coords is not None, (
            'Received not compatible Point "{}"'.format(repr(point))
        )
        if coords:
            if isinstance(coords[0], Iterable):
                return list(coords[0])
            return coords
        return []

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            loaded = loads(node.value)
            if isinstance(loaded, geometry.Point):
                return loaded

        if isinstance(node, ast.ListValue):
            inner_values = [float(v.value) for v in node.values]
            return geometry.Point(*inner_values)

    @staticmethod
    def parse_value(coords):
        if not isinstance(coords, Iterable):
            raise Exception("Received incompatible value for Point")

        return geometry.Point(*coords)
