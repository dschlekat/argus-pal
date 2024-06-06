"""
This script is used to test the get_times method in the evr_inputs.py file.
Outputs the times to the testing/input_test_results.txt file for testing.
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inputs import Input
from astropy.coordinates import SkyCoord
import astropy.units as u

# Gets the ra range
date = "2024-03-31"
_input = Input()
ra_min, ra_max = _input.get_ra_range(date)

ra_min = SkyCoord(ra=ra_min*u.deg, dec=0, unit="deg")
ra_max = SkyCoord(ra=ra_max*u.deg, dec=0, unit="deg")

ra_min_hms = ra_min.to_string('hmsdms')
ra_max_hms = ra_max.to_string('hmsdms')

print(f"RA range for {date}: {ra_min_hms} to {ra_max_hms}")
