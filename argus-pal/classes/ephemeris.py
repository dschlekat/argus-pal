"""
UNFINISHED

This module contains the ephemeris class, which is used to query the Lowell Observatory ephemeris tool for asteroid locations throughout the nights of observation.
It allows the user to input dates manually or use a preset file containing a list of dates.
The results are written to a file for further analysis.
"""
from classes.query import Input
from classes.propogate import Propogate
import os
import time
import datetime
import json
import sys
from tqdm import tqdm

class Ephemeris:
    observatory = None # 3char observatory code 
    calculation_mode = None # 0 for fast, 1 for accurate
    input_mode = None # 0 for txt input, 1 for manual

    def __init__(self, observatory=None, calculation_mode=None, input_mode=None):
        if observatory is None:
            self.observatory = 256
        if calculation_mode is None:
            self.calculation_mode = 0
        if input_mode is None:
            self.input_mode = 0

    def txt_input(self, path):
        _input = Input()
        propogate = Propogate()

        if path == "d":
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/all_dates_PF.txt")

        # Get the dates from the preset file
        dates = _input.get_dates(path)

        begin_time = time.time()

        begin_time = time.time()

        try :
            # Loop through the dates and query the database
            date_loop = tqdm(dates, desc="Iterating through specified dates...", leave=False)
            for date in date_loop:
                file_path = propogate.file_path(date)

                start_time = time.time()

                # Collect the list of asteroids
                propogate.get_asteroids(file_path)

                ephemera = {
                    "observable_asteroids": []
                }

                if self.calculation_mode == 0:
                    ephemera = propogate.propogate_rate(600, 30, date)
                elif self.calculation_mode == 1:
                    ephemera = propogate.propogate_lowell(date, self.observatory)

                json_string = json.dumps(ephemera, indent=4)

                # Write the results to a file
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data/eph_{date}.txt")
                with open(file_path, "w") as f:
                    f.write(json_string)

                end_time = time.time()

                desc = f"Asteroid positions propogated for {date}. Time elapsed: {end_time - start_time:.2f} seconds. Starting next date"
                date_loop.set_description(desc, refresh=True)
        
        except KeyboardInterrupt:
            print("\n")
            print("Keyboard interrupt activated. Quitting...")
            sys.exit(0)

        final_time = time.time()
        print("Program complete.")
        print(f"Total time elapsed: {final_time - begin_time:.2f} seconds. \n")

    def manual_input(self, date):
        propogate = Propogate()

        file_path = propogate.file_path(date)

        print("\n")
        print(f"Propogating asteroid positions for {date}: \n")

        start_time = time.time()

        # Collect the list of asteroids
        propogate.get_asteroids(file_path)

        ephemera = {
            "observable_asteroids": []
        }

        try:
            # Conduct the propogation
            if self.calculation_mode == 0:
                ephemera = propogate.propogate_rate(600, 30, date)
            elif self.calculation_mode == 1:
                ephemera = propogate.propogate_lowell(date, self.observatory)

            json_string = json.dumps(ephemera, indent=4)

            # Write the results to a file
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data/eph_{date}.txt")
            with open(file_path, "w") as f:
                f.write(json_string)

        
        except KeyboardInterrupt:
            print("\n")
            print("Keyboard interrupt activated. Quitting...")
            sys.exit(0)

        end_time = time.time()
        print("Program complete. Results written to file.")
        print(f"Total time elapsed: {end_time - start_time:.2f} seconds. \n")