from astropy.time import Time
from datetime import datetime, timedelta
import json
import os

from pal.astorb.pipeline import pipeline
from pal.astorb.propogate import propogate
from pal.utils.asteroid import Asteroid
from pal.utils.telescope import Telescope

"""
    This script is used to query the Lowell Observatory Astorb database to determine
    what asteroids are visible in the sky at the time of observation.
    A list of asteroids, along with their brightness and any irregularity flags are logged.
    The asteroid locations are then propogated for every 15 minutes throughout the night.
"""

def execute(**kwargs):
    """ Execute the ephemeris action with the given parameters.
    :param kwargs: Accepted parameters for the action:
            - telescope: The name of the telescope to use. Check the configuration file for available telescopes.
            - start_date: The start date for the observation period.
            - end_date: The end date for the observation period.
            - mag_lim: Whether to apply a magnitude limit to the query. Default is False. If set to True, the tool will only return asteroids with a magnitude less than or equal to the limit, which is set by the telescope.
            - propogation_interval: The interval at which to propogate the asteroid locations throughout the night. Default is 15 minutes.
    :return: 0 if successful, 1 if an error occurred.
    """
    if os.path.exists("pal/results/ephemera") == False:
        os.makedirs("pal/results/ephemera")
    if os.path.exists("pal/results/logs") == False:
        os.makedirs("pal/results/logs")
    if os.path.exists("pal/results/observable") == False:
        os.makedirs("pal/results/observable")

    results = query_asteroids(**kwargs)
    ephemera = propogate_asteroids(results, **kwargs)
    
    return log_results(ephemera, **kwargs)

def query_asteroids(**kwargs) -> list[str]:
    """ Query the Lowell Observatory Astorb database for asteroids visible in the sky at the time of observation.
    :param kwargs: the parameters used for the action
    :return: a list of file paths to the results
    """
    dates = create_dates(kwargs['start_date'], kwargs['end_date'])
    telescope = Telescope(kwargs['telescope'])

    results = pipeline(dates, telescope, kwargs['mag_lim'])
    return results


def propogate_asteroids(results, **kwargs):
    """ Propogate the asteroid locations for every 15 minutes throughout the night.
    :param asteroids: the list of asteroids to propogate
    :param kwargs: the parameters used for the action
    """
    results = propogate(results)
    return results


def create_dates(start_date: datetime, end_date: datetime) -> list[datetime]:
    """ Create a list of dates between the start and end dates.
    :param start_date: the start date in the format YYYY-MM-DD
    :param end_date: the end date in the format YYYY-MM-DD
    :return: a list of dates between the start and end dates
    """
    start, end = check_date_format(start_date, end_date)    

    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    dates = Time(dates, format='datetime', scale='utc')

    return dates

def check_date_format(start_date: str, end_date: str) -> tuple[datetime, datetime]:
    """ Check the format of the start and end dates.
    :param start_date: the start date in the format YYYY-MM-DD
    :param end_date: the end date in the format YYYY-MM-DD
    :return: the start and end dates as datetime objects
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    if start > end:
        raise ValueError("Start date must be before end date.")
    
    if start < datetime.now():
        raise ValueError("Start date must be in the future.")
    
    return start, end

def log_results(ephemera, **kwargs):
    """ Log the results of the ephemeris action to a file.
    :param ephemera: the list of files containing the ephemeris data
    :param kwargs: the parameters used for the action
    :return: 0 if successful, 1 if an error occurred
    """
    start_str = kwargs['start_date']
    end_str = kwargs['end_date']
    telescope = kwargs['telescope']
    file_name = f"pal/results/logs/{telescope}_{start_str}_to_{end_str}.txt"
    with open(file_name, 'w') as f:
        f.write(f"Ephemera successfully generated for {telescope} between the dates of {start_str} and {end_str}. \n")
        f.write("Ephemera data available at the following file paths: \n")
        for file in ephemera:
            f.write(file)
            f.write('\n')
        return 0