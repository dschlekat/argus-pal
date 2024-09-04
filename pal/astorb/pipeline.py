from datetime import datetime
import json
import numpy as np
import os
import time
from tqdm import tqdm

from pal.astorb.query import Query
from pal.utils.telescope import Telescope

"""
    This script is the main pipeline for the target finding program. 
    It allows the user to input dates manually or use a preset file to query the database for targets.
    The results are written to a file for further analysis.
"""

# TODO: Fix query retrying
# TODO: Fix total observable asteroid count comment

def pipeline(dates: list[datetime], telescope: Telescope, mag_lim: bool) -> list[str]:
    """ Query the Lowell Observatory Astorb database for asteroids visible in the sky at the time of observation.
    :param dates: the dates to query the database for
    :param telescope: the telescope to use for the query
    :return: a list of asteroids visible in the sky at the time of observation
    """

    if mag_lim:
        v_mag = telescope.mag_lim
    else:
        v_mag = 30

    files = []
    total_asteroids = 0

    loop = tqdm(dates, desc="Querying database", leave=False)
    for date in loop:
        file_name = already_queried(date, telescope)
        if file_name != False:
            files.append(file_name)
            loop.set_description(f"Data for {date} already queried. Skipping.", refresh=True)
            continue
        

        start_time = time.time()

        query = Query()

        # Get the sky range for the given date
        b_ra_min, b_ra_max, b_dec_min, b_dec_max = get_sky_range(date, telescope)

        # Build the query and get the results
        query.build_query(ra_min=b_ra_min, ra_max=b_ra_max, dec_min=b_dec_min, dec_max=b_dec_max, date=date, mag_lim=v_mag)
        query.get_results()

        if not query.response.ok:
            raise ValueError("Query error: ", query.response)

        data = query.response.json()['data']['ephemeris']
        num_asteroids = len(data)
        total_asteroids += num_asteroids

        continue_query = True
        while continue_query:
            if num_asteroids == 1000:
                #requery for the same date with the last asteroid id as the new limit
                last_id = data[-1]['minorplanet']['ast_number']
                query.build_query(ra_min=b_ra_min, ra_max=b_ra_max, dec_min=b_dec_min, dec_max=b_dec_max, date=date, mag_lim=v_mag, last_id=last_id)
                query.get_results()
                data.extend(query.response.json()['data']['ephemeris'])
                num_asteroids = len(data)
                total_asteroids = total_asteroids + num_asteroids
            else:
                continue_query = False

        # Write the results to a file
        files.append(log_obserbable_asteroids(data, date, telescope.slug))

        end_time = time.time()
        date_str = date.strftime("%Y-%m-%d")
        desc = f"Ephemeris data for {date_str} written to file. {num_asteroids} asteroids observable. Time elapsed: {end_time - start_time:.2f} seconds. "
        loop.set_description(desc, refresh=True)

    if total_asteroids != 0:
        desc = f"Ephemera complete. Total of {total_asteroids} asteroids observable."
    else:
        desc = "Ephemera complete. All dates have already been queried. "
    loop.set_description(desc, refresh=True)
    print(loop)

    return files

def get_sky_range(date: datetime, telescope: Telescope) -> tuple[float, float, float, float]:
    """ Get the right ascension and declination range for the given date.
    :param date: the date to calculate the range for
    :param telescope: the telescope to calculate the range for
    :return: the right ascension and declination range for the given date
    """
    # Collect the right ascension range for the date
    ra_min, ra_max = telescope.get_ra_range(date)
    dec_min, dec_max = telescope.get_dec_range()

    # Add buffer to the ra and dec values, convert to radians
    b_ra_min = (ra_min - 5) * np.pi / 180
    b_ra_max = (ra_max + 5) * np.pi / 180
    b_dec_min = (dec_min - 5) * np.pi / 180
    b_dec_max = (dec_max + 5) * np.pi / 180

    return b_ra_min, b_ra_max, b_dec_min, b_dec_max

def log_obserbable_asteroids(data: list[dict], date: datetime, slug: str) -> str:
    """ Write the observable asteroids to a file.
    :param data: the data to write to the file
    :param date: the date the data was collected
    """
    # Create the file name
    date_str = date.strftime("%Y-%m-%d")
    file_name = f"pal/results/observable/{slug}_{date_str}.json"

    # Write the data to the file
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

    return file_name

def already_queried(date: datetime, telescope: Telescope) -> bool:
    date_str = date.strftime("%Y-%m-%d")
    file_name = f"pal/results/observable/{telescope.slug}_{date_str}.json"
    if os.path.exists(file_name):
        return file_name
    else:
        return False