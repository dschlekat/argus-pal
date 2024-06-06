"""
This script is the main pipeline for the target finding program. 
It allows the user to input dates manually or use a preset file to query the database for targets.
The results are written to a file for further analysis.
"""
from classes.inputs import Input
from classes.query import Query
import os
import numpy as np
import time
import datetime
import json
import sys
from tqdm import tqdm

# Firm Query Parameters
v_mag_1 = 16      ## limiting magnitude for 1s Pathfinder exposures
dec_min = -20     ## minimum declination for Pathfinder, in degrees
dec_max = 72      ## maximum declination for Pathfinder, in degrees
limit = 1000      ## maximum number of asteroids to return in a query

# Main function to run the program
def main():
    mode = -1

    # Get the mode of input
    while mode < 0:
        try:
            mode = int(input("Enter 0 for txt input, 1 for manual: "))
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Run the appropriate function
    if mode == 0:
        txt_input()
    elif mode == 1:
        manual_date()
    else:
        print("Invalid mode. Quitting...")
        return


# Preset dates input and query using the input file
def txt_input():
    _input = Input()
    query = Query()

    mode = str(input("Enter file path, or d for default: "))
    if mode == "d":
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/all_dates_PF.txt")
    else:
        path = mode

    # Get the dates from the preset file
    dates = _input.get_dates(path)

    begin_time = time.time()

    try :
        # Loop through the dates and query the database

        loop = tqdm(dates, desc="Querying database", leave=False)
        for date in loop:
            start_time = time.time()

            # Collect the right ascension range for the date
            ra_min, ra_max = _input.get_ra_range(date)

            # Add buffer to the ra and dec values, convert to radians
            b_ra_min = (ra_min - 5) * np.pi / 180
            b_ra_max = (ra_max + 5) * np.pi / 180
            b_dec_min = (dec_min - 5) * np.pi / 180
            b_dec_max = (dec_max + 5) * np.pi / 180

            # Build the query and get the results
            query.build_query(ra_min=b_ra_min, ra_max=b_ra_max, dec_min=b_dec_min, dec_max=b_dec_max, date=date, mag_lim=v_mag_1, limit=limit)
            query.get_results()
            data = query.response.json()

            # Convert the dictionary to a JSON string
            json_string = json.dumps(data, indent=4)

            # Writes the results to a file
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data/obs_ast_{date}.txt")
            with open(file_path, "w") as f:
                f.write(json_string)

            num_asteroids = len(query.response.json()['data']['ephemeris'])
            end_time = time.time()
            desc = f"Ephemeris data for {date} written to file. {num_asteroids} asteroids observable. Time elapsed: {end_time - start_time:.2f} seconds."
            loop.set_description(desc, refresh=True)

            if num_asteroids == 1000:
                loop.set_description("WARNING: Maximum limit of 1000 asteroids reached. Missing data.", refresh=True)
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n")
        print("Keyboard interrupt activated. Quitting...")
        sys.exit(0)

    final_time = time.time()
    print(f"Total time elapsed: {final_time - begin_time:.2f} seconds. \n")

        


# Manual date input and query
def manual_date():
    _input = Input()
    query = Query()

    date = str(input("Enter the date (YYYY-MM-DD), or \"t\" for today: "))
    if date == "t":
        date = str(datetime.date.today())

    start_time = time.time()

    # Collect the right ascension range for the date
    ra_min, ra_max = _input.get_ra_range(date)

    # Add buffer to the ra and dec values, convert to radians
    b_ra_min = (ra_min - 5) * np.pi / 180
    b_ra_max = (ra_max + 5) * np.pi / 180
    b_dec_min = (dec_min - 5) * np.pi / 180
    b_dec_max = (dec_max + 5) * np.pi / 180

    try:
        # Build the query and get the results
        query.build_query(ra_min=b_ra_min, ra_max=b_ra_max, dec_min=b_dec_min, dec_max=b_dec_max, date=date, mag_lim=v_mag_1, limit=limit)
        query.get_results()
        data = query.response.json()

        # Convert the dictionary to a JSON string
        json_string = json.dumps(data, indent=4)

        # Writes the results to a file
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data/obs_ast_{date}.txt")
        with open(file_path, "w") as f:
            f.write(json_string)

        num_asteroids = len(query.response.json()['data']['ephemeris'])
        end_time = time.time()
        print(f"Ephemeris data for {date} written to file. {num_asteroids} asteroids observable.")
        print(f"Time elapsed: {end_time - start_time:.2f} seconds. \n")

        if num_asteroids == 1000:
            print("WARNING: Maximum limit of 1000 asteroids reached. Some may not be displayed.")
    
    except KeyboardInterrupt:
        print("\n")
        print("Keyboard interrupt activated. Quitting...")
        sys.exit(0)

if __name__ == "__main__":
    main()