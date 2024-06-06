"""
This file contains the Input class, which is used to parse input dates and return right ascension query parameters.
Has the functions:
    __init__(): Initializes the Input object.
    get_dates(file_path): Collects dates from a file given a file path.
    get_ra_range(date): Gets the visible right ascension range for Pathfinder for a given date.
"""
from astropy.time import Time
from astropy.coordinates import EarthLocation
import astropy.units as u


class Input():
    input = None
    dates = None
    pari_loc = None


    def __init__(self):
        # Init function, sets the location of the PARI observatory
        self.pari_loc = EarthLocation(lat=35.1983*u.deg, lon=-82.8197*u.deg, height=2898*u.m)


    # Collects dates from a file given a file path
    def get_dates(self, file_path):
        # Open the file and read the dates
        try:
            with open(file_path, 'r') as f:
                self.dates = f.read().splitlines()
                return self.dates
        except Exception as e:
            raise IOError(f"Error reading dates file: {e}")
    

    # Get the right ascension range for the given date
    def get_ra_range(self, date):
        # Get the LST at UTC midnight for the given date
        u_mid = Time(date, format='iso', scale='utc')
        lst = u_mid.sidereal_time('mean', longitude=self.pari_loc.lon)

        # Get the RA query range for the given LST @ UTC midnight
        ra_min = lst.deg + (1 * 15)   # 1 hour after midnight
        ra_max = lst.deg + (9 * 15)   # 9 hours after midnight

        return ra_min, ra_max
    