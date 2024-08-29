from astropy.coordinates import AltAz, EarthLocation, get_sun
from astropy.time import Time
import astropy.units as u
import configparser
import datetime

"""
    Contains the Telescope class, which is used to represent the desired instrument to be used for observability calculations.
"""

# TODO get_night_length is broken

class Telescope():

    def __init__(self, telescope: str):
        self.name = telescope

        # Read the telescope configuration file
        config = configparser.ConfigParser()
        config.read('config/telescopes.ini')

        # Get the telescope parameters
        self.latitude = config[telescope]['latitude']
        self.longitude = config[telescope]['longitude']
        self.altitude = config[telescope]['altitude']

        # Set the location
        self.location = EarthLocation(lat=self.latitude*u.deg, lon=self.longitude*u.deg, height=self.altitude*u.m)

        # Set the default values
        self.dec_min = config[telescope]['dec_min']
        self.dec_max = config[telescope]['dec_max']
        if telescope == 'pathfinder':
            self.mag_lim = config[telescope]['bright_limiting_magnitude']
        else:
            self.mag_lim = config[telescope]['limiting_magnitude']

    def get_lST(self, date: Time) -> Time:
        """ Get the Local Sidereal Time at UTC midnight for the given date.
        :param date: the date to calculate the LST for
        :return: the LST at UTC midnight for the given date
        """
        u_mid = Time(date, format='iso', scale='utc')
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

        night_start_time = Time(night_start).datetime.time()
        night_end_time = Time(night_end).datetime.time()

        return night_start_time, night_end_time
    
    def get_ra_range(self, date: Time) -> tuple[float, float]:
        """ Get the right ascension range for the given date.
        This function is exclusive to the Pathfinder telescope.
        :param date: the date to calculate the right ascension range for
        :return: the right ascension range for the given date
        """
        if self.location == None:
            raise ValueError("Telescope location not set")
        if self.name != 'pathfinder':
            raise ValueError("RA range only available for Pathfinder telescope")
        
        lst = self.get_lST(date)
        night_start, night_end = self.get_night_length(date)
        
        # Get the RA query range for the given LST @ UTC midnight
        ra_min = lst.deg + (night_start.hours + night_start.minutes/60) * 15 
        ra_max = lst.deg + (night_end.hours + night_end.minutes/60) * 15 

        return ra_min, ra_max

        

