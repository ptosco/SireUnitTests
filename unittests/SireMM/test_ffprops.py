
from Sire.MM import *
from Sire.Base import *

def _pvt_test_props(ff, verbose = False):

    try:
        ff.setCLJFunction( CLJShiftFunction() )
        ff.setCLJFunction("f", CLJRFFunction())
        ff.setCLJFunction("next", CLJSoftShiftFunction())
    except:
        ff.setCLJFunction( CLJIntraShiftFunction() )
        ff.setCLJFunction("f", CLJIntraRFFunction() )
        ff.setCLJFunction("next", CLJSoftIntraShiftFunction())

    if verbose:
        print("Testing %s" % ff)

    ff.setProperty("dielectric[f]", wrap(2))

    d = ff.property("dielectric[f]")

    assert( d == 2 )

    ff.setProperty("dielectric[all]", wrap(3))

    d = ff.property("dielectric[f]")

    assert( d == 3 )

    ff.setProperty("combiningRules[all]", wrap("geometric"))
    assert( ff.property("combiningRules") == "geometric" )
    assert( ff.property("combiningRules[default]") == "geometric" )
    assert( ff.property("combiningRules[f]") == "geometric" )

    ff.setProperty("combiningRules", wrap("arithmetic"))
    assert( ff.property("combiningRules") == "arithmetic" )
    assert( ff.property("combiningRules[default]") == "arithmetic" )
    assert( ff.property("combiningRules[f]") == "geometric" )

    ff.setProperty("combiningRules[default]", wrap("geometric"))
    assert( ff.property("combiningRules") == "geometric" )
    assert( ff.property("combiningRules[default]") == "geometric" )
    assert( ff.property("combiningRules[f]") == "geometric" )

    ff.setProperty("combiningRules[all]", wrap("arithmetic"))
    assert( ff.property("combiningRules") == "arithmetic" )
    assert( ff.property("combiningRules[default]") == "arithmetic" )
    assert( ff.property("combiningRules[f]") == "arithmetic" )

    ff.setProperty("alpha[all]", VariantProperty(5.0))
    assert( ff.property("alpha[next]") == 5.0 )

    ff.setProperty("alpha[next]", wrap(2.0))
    assert( ff.property("alpha[next]") == 2.0 )

def test_props(verbose=False):
    ff = InterFF()

    _pvt_test_props(ff, verbose)

    ff = InterGroupFF()

    _pvt_test_props(ff, verbose)

    ff = IntraFF()

    _pvt_test_props(ff, verbose)

    ff = IntraGroupFF()

    _pvt_test_props(ff, verbose)

if __name__ == "__main__":
    test_props(True)
