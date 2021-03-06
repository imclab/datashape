"""
Type visitor that reconstructs types.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from itertools import starmap

from .coretypes import Mono, Unit, type_constructor


def descend(t):
    """Determine whether to descend down the given term (which is a type)"""
    return isinstance(t, Mono) and not isinstance(t, Unit)


def transform(visitor, t, descend=descend):
    """
    Transform a type to recreate a new type
    """
    if isinstance(t, Mono):
        fn = getattr(visitor, type(t).__name__, None)
        if fn is not None:
            return fn(t)
        elif descend(t):
            tcon = type_constructor(t)
            return tcon(*[transform(visitor, p) for p in t.parameters])

    return t


def tmap(f, t, descend=descend):
    """
    Map f over t, calling `f` with type `t`. Reconstructs a new type with
    the results from `f`.
    """
    if descend(t):
        tcon = type_constructor(t)
        t = tcon(*[tmap(f, p) for p in t.parameters])
    return f(t)


def tzip(f, a, b, descend=descend):
    """Map f over two types zip-wise"""
    from . import verify # TODO: remove circularity

    if not descend(a) or not descend(b):
        return a, b

    verify(a, b)
    result = zip(*starmap(f, zip(a.parameters, b.parameters)))
    params1, params2 = result or [(), ()]
    return (type_constructor(a)(*params1), type_constructor(b)(*params2))


def traverse(f, t):
    """
    Map f over t, calling `f` with type `t` and the map result of the mapping
    `f` over `t`s parameters.
    """
    if descend(t):
        return f(t, [traverse(f, p) for p in t.parameters])
    return t
