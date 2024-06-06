"""
This script is used to query the Lowell Observatory ephemeris tool for asteroid locations throughout the nights of observation.
It allows the user to input dates manually or use a preset file containing a list of dates.
The results are written to a file for further analysis.
"""
from classes.inputs import Input
from classes.propogate import Propogate
import os
import time
import datetime
import json
import sys
from tqdm import tqdm


# Firm Propogation Parameters
observatory = 256 ## observatory code for GBO
calculation_mode = -1

# Main function to run the program
def main():
    global calculation_mode

    # Get the mode of calculation
    while calculation_mode < 0:
        try:
            calculation_mode = int(input("Enter 0 for manual calculation (fast), or 1 for Lowell calculation (accurate): "))
        except ValueError:
            print("Invalid input. Please enter a number.")

    if calculation_mode != 0 and calculation_mode != 1:
        print("Invalid mode. Quitting...")
        return


    input_mode = -1

    # Get the mode of input
    while input_mode < 0:
        try:
            input_mode = int(input("Enter 0 for txt input, 1 for manual: "))
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Run the appropriate function
    if input_mode == 0:
        txt_input()
    elif input_mode == 1:
        manual_date()
    else:
        print("Invalid input mode. Quitting...")
        return


# Preset dates input and query using the input file
def txt_input():
    _input = Input()
    propogate = Propogate()

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
        date_loop = tqdm(dates, desc="Iterating through specified dates...", leave=False)
        for date in date_loop:
            file_path = propogate.file_path(date)

            start_time = time.time()

            # Collect the list of asteroids
            propogate.get_asteroids(file_path)

            ephemera = {
                "observable_asteroids": []
            }

            if calculation_mode == 0:
                ephemera = propogate.propogate_rate(600, 30, date)
            elif calculation_mode == 1:
                ephemera = propogate.propogate_lowell(date, observatory)

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


# Manual date input and propogation
def manual_date():
    propogate = Propogate()

    date = str(input("Enter the date (YYYY-MM-DD), or \"t\" for today: "))
    if date == "t":
        date = str(datetime.date.today())
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
        if calculation_mode == 0:
            ephemera = propogate.propogate_rate()
        elif calculation_mode == 1:
            ephemera = propogate.propogate_lowell(date, observatory)

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

if __name__ == "__main__":
    main()