"""
    Test the result of different simplification
"""

from simplification.DPTS import DPTS_approx
from simplification.IriImai import IriImai
from simplification.ATS import NP_ATS, ATS
from simplification.DouglasPeucker import DP
from simplification.error import CED, SED, V_ERROR

trajectory = [{'y': 24.78945, 'x': 120.99995},{'y': 24.78943, 'x': 121.00055},{'y': 24.78942, 'x': 121.00111},{'y': 24.78934, 'x': 121.00171},{'y': 24.78915, 'x': 121.00225},{'y': 24.78895, 'x': 121.00272},{'y': 24.78894, 'x': 121.00333},{'y': 24.78937, 'x': 121.00369},{'y': 24.78984, 'x': 121.00409},{'y': 24.7903,  'x': 121.00442},{'y': 24.79112, 'x': 121.0044 },{'y': 24.79171, 'x': 121.00373},{'y': 24.79216, 'x': 121.00307},{'y': 24.79231, 'x': 121.00286},{'y': 24.79245, 'x': 121.00266},{'y': 24.79258, 'x': 121.00251},{'y': 24.79267, 'x': 121.00234},{'y': 24.7929,  'x': 121.00198},{'y': 24.79341, 'x': 121.0012 },{'y': 24.79394, 'x': 121.00055},{'y': 24.79458, 'x': 120.99971},{'y': 24.79536, 'x': 120.99877},{'y': 24.79607, 'x': 120.99798}]

print "test ATS"
S_ATS = ATS(trajectory, 0.5)
print "test NP-ATS"
S_NPATS = NP_ATS(trajectory, 0.5)
print "test Douglas-Peucker"
S_DP = DP(trajectory, 0.0001)
print "test Iri-Imai"
S_II = IriImai(trajectory, 0.0001)
print "test DPTS"
S_DPTS = DPTS_approx(trajectory, 0.2)

print "position error"
print CED(trajectory, S_DPTS)
print SED(trajectory, S_DPTS)
print V_ERROR(trajectory, S_DPTS)