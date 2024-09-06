from astropy.coordinates import AltAz, EarthLocation, get_sun
from astropy.time import Time
import astropy.units as u
from datetime import datetime

from pal.utils import config

"""
    Contains the Telescope class, which is used to represent the desired instrument to be used for observability calculations.
"""

# DONE: Fix times in time-dependent classes.
# TODO: Remove datetime dependency

class Telescope():

    def __init__(self, telescope: str):
        self.name = telescope

        # Read the telescope configuration file
        settings = config.read('pal/config/telescope.ini')

        # Get the telescope parameters
        self.slug = config.get(settings, telescope, 'slug')
        self.slug = config.expected_type(self.slug)
        self.latitude = config.get(settings, telescope, 'latitude')
        self.latitude = config.expected_type(self.latitude)
        self.longitude = config.get(settings, telescope, 'longitude')
        self.longitude = config.expected_type(self.longitude)
        self.altitude = config.get(settings, telescope, 'altitude')
        self.altitude = config.expected_type(self.altitude)
        self.dec_min = config.get(settings, telescope, 'dec_min')
        self.dec_min = config.expected_type(self.dec_min)
        self.dec_max = config.get(settings, telescope, 'dec_max')
        self.dec_max = config.expected_type(self.dec_max)

        # Set the location
        self.location = EarthLocation(lat=self.latitude*u.deg, lon=self.longitude*u.deg, height=self.altitude*u.m)

        if telescope == 'Pathfinder':
            self.mag_lim = config.get(settings, telescope, 'bright_limiting_magnitude')
            self.mag_lim = config.expected_type(self.mag_lim)
        else:
            self.mag_lim = config.get(settings, telescope, 'limiting_magnitude')
            self.mag_lim = config.expected_type(self.mag_lim)

    def get_lST(self, date: Time) -> Time:
        """ Get the Local Sidereal Time at UTC midnight for the given date.
        :param date: the date to calculate the LST for
        :return: the LST at UTC midnight for the given date
        """
        u_mid = date
        lst = u_mid.sidereal_time('mean', longitude=self.location.lon)
        return lst
    
    def get_night_length(self, date: Time) -> tuple[Time, Time]:
        """ Get the start and end times of the astronomical night for the given date.
        :param date: the date to calculate the night length for
        :return: the start and end times of the astronomical night for the given date
        """
        times = date + (u.Quantity(range(0, 24*60, 1), u.minute))
        altaz = AltAz(location=self.location, obstime=times)

        # Calculate the Sun's altitude at each time
        sun_altitudes = get_sun(times).transform_to(altaz).alt

        # Find when the Sun crosses -18 degrees altitude
        night_start = times[sun_altitudes < -18*u.deg][0].iso
        night_end = times[sun_altitudes < -18*u.deg][-1].iso

        night_start_time = Time(night_start).datetime
        night_end_time = Time(night_end).datetime

        return night_start_time, night_end_time
    
    def get_ra_range(self, date: datetime) -> tuple[float, float]:
        """ Get the right ascension range for the given date. This function is exclusive to the Pathfinder telescope.
        :param date: the date to calculate the right ascension range for
        :return: the right ascension range for the given date
        """
        if self.location == None:
            raise ValueError("Telescope location not set")
        if self.name != 'Pathfinder':
            raise ValueError("RA range only available for Pathfinder telescope")
        
        date = Time(date, format='datetime', scale='utc')
        lst = self.get_lST(date)

        night_start, night_end = self.get_night_length(date)
        ra_min = lst.deg + (night_start.hour + night_start.minute/60) * 15 
        ra_max = lst.deg + (night_end.hour + night_end.minute/60) * 15 

        return ra_min, ra_max
    
    def get_dec_range(self) -> tuple[float, float]:
        """ Get the declination range for the telescope. 
        :return: the declination range for the telescope
        """
        # Note that this declination range is hardcoded for the Pathfinder telescope.
        # Future scopes could have date-dependent declination ranges.
        if self.name == 'Pathfinder':
            return self.dec_min, self.dec_max
        else:
            raise ValueError("Unsupported telescope.")
    

        

