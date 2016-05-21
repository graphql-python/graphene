from functools import partial
from itertools import chain

from promise import Promise


def promise_middleware(func, middlewares):
    middlewares = chain((func, make_it_promise), middlewares)
    past = None
    for m in middlewares:
        past = partial(m, past) if past else m

    return past


def make_it_promise(next, *a, **b):
    return Promise.resolve(next(*a, **b))
