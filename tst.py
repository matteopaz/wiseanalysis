import astropy 
import astroquery
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import time
import responses

c = SkyCoord("148.80084508 69.0652157", unit=(astropy.units.deg, astropy.units.deg), frame='icrs')
rad = 4 * astropy.units.arcsec
t1 = time.time()
r= Simbad.query_region(c, radius=rad)
print(r)
if r:
    print("found")