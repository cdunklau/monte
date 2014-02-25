"""
Objects used by Monte syntax expansions.
"""
from monte.runtime.base import MonteObject, ejector, throw
from monte.runtime.data import false, String, Integer, bwrap
from monte.runtime.flow import getIterator
from monte.runtime.tables import ConstList, mapMaker


def validateFor(flag):
    if not flag:
        raise RuntimeError("For-loop body isn't valid after for-loop exits.")

def accumulateList(coll, obj):
    it = getIterator(coll)
    acc = []
    skip = ejector("listcomp_skip")
    for key, item in it:
        try:
            acc.append(obj.run(key, item, skip))
        except skip._m_type:
            continue
    return ConstList(acc)

def accumulateMap(coll, obj):
    return mapMaker.fromPairs(accumulateList(coll, obj))

def iterWhile(f):
    return (v for v in iter(f, false))

class Comparer(MonteObject):
    def greaterThan(self, left, right):
        return bwrap(left > right)

    def geq(self, left, right):
        return bwrap(left >= right)

    def lessThan(self, left, right):
        return bwrap(left < right)

    def leq(self, left, right):
        return bwrap(left <= right)

    def asBigAs(self, left, right):
        return bwrap((left <= right) and (left >= right))

comparer = Comparer()


class MakeVerbFacet(MonteObject):
    _m_fqn = "__makeVerbFacet$verbFacet"
    def curryCall(self, obj, verb):
        if not isinstance(verb, String):
            raise RuntimeError("%r is not a string" % (verb,))
        def facet(*a):
            return getattr(obj, verb.s)(*a)
        return facet

makeVerbFacet = MakeVerbFacet()

def matchSame(expected):
    def sameMatcher(specimen, ej):
        #XXX equalizer
        if specimen == expected:
            return expected
        else:
            ej("%r is not %r" % (specimen, expected))
    return sameMatcher

def switchFailed(specimen, *failures):
    raise RuntimeError("%s did not match any option: [%s]" % (
        specimen,
        " ".join(str(f) for f in failures)))

_absent = object()
def suchThat(x, y=_absent):
    if y is _absent:
        # 1-arg invocation.
        def suchThatMatcher(specimen, ejector):
            if not x:
                ejector("such-that expression was false")
        return suchThatMatcher
    else:
        return [x, None]

def extract(x, instead=_absent):
    if instead is _absent:
        # 1-arg invocation.
        def extractor(specimen, ejector):
            value = specimen[x]
            without = dict(specimen)
            del without[x]
            return [value, without]
        return extractor
    else:
        def extractor(specimen, ejector):
            value = specimen.get(x, _absent)
            if value is _absent:
                return [instead(), specimen]
            without = dict(specimen)
            del without[x]
            return [value, without]
        return extractor

class Empty:
    def coerce(self, specimen, ej):
        if len(specimen) == 0:
            return specimen
        else:
            throw.eject(ej, "Not empty: %s" % specimen)

def splitList(cut):
    if not isinstance(cut, Integer):
        raise RuntimeError("%r is not an integer" % (cut,))
    cut = cut.n
    def listSplitter(specimen, ej):
        #XXX coerce to list
        if len(specimen) < cut:
            throw.eject(ej, "A %s size list doesn't match a >= %s size list pattern" % (len(specimen), cut))
        return specimen[:cut] + (specimen[cut:],)

    return listSplitter


class BooleanFlow(MonteObject):
    _m_fqn = "__booleanFlow"
    def broken(self):
        #XXX should return broken ref
        return object()

    def failureList(self, size):
        #XXX needs broken ref
        if not isinstance(size, Integer):
            raise RuntimeError("%r is not an integer" % (size,))
        return [false] + [object()] * size.n

booleanFlow = BooleanFlow()