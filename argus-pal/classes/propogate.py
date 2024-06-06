"""
Contains the Propogate class, which is used to determine asteroid locations throughout the night.
Has the functions:
    __init__(): Initializes the Propogate object.
    get_asteroids(): Collects the asteroids from the result txt files.
    build_url(): Builds the query url based on the inputs.
    get_results(): Posts the query and returns the results.
"""
import json
import numpy as np
import requests
import time
import datetime
from tqdm import tqdm

class Propogate():
    asteroids = None
    url = None
    response = None
    data = None


    def __init__(self):
        pass

    
    # Builds a file path based on the date
    def file_path(self, date):
        return f"data/obs_ast_{date}.txt"


    # Collects the asteroids from the result txt files
    def get_asteroids(self, file_path):
        try:
            with open(file_path) as file:
                eph = json.load(file)
                self.asteroids = eph['data']['ephemeris']
        except Exception as e:
            raise IOError(f"Error reading asteroids file: {e}")


    # Builds the query url based on the inputs
    def url_builder(self, mpc, observatory, date, duration=600, step=30):
        self.url = f"https://asteroid.lowell.edu/api/ephemeris/generate?asteroid={mpc}&observatory={observatory}&start-utc={date}T00:00&duration-minutes={duration}&step-minutes={step}"


    # Posts the query and returns the results
    def get_results(self, max_retries=5):
        retry_count = 0
        try:
            # Retry the request if it fails
            while retry_count < max_retries:
                # Post the query
                self.response = requests.get(self.url)

                # Check if the response is successful and not empty
                if self.response.status_code == 200:
                    try:
                        self.data = self.response.json()
                        if self.data:
                            return # Return if the response is successful
                        else:
                            print("Received empty JSON response. Retrying...")
                    except ValueError:  # includes simplejson.decoder.JSONDecodeError
                        print("Failed to decode JSON. Retrying...")
                elif self.response.status_code == 400:
                    print("Bad request. Check the query and try again.")
                    return
                elif self.response.status_code == 504:
                    print("Gateway timeout. Retrying...")
                else:
                    print(f"Request failed with status code: ", self.response.status_code)

                retry_count += 1
                time.sleep(1 + retry_count)  # Wait for 1+ seconds before retrying, to not overwhelm the server
        except Exception as e:
            raise IOError("Error posting query: {e}")


    # Propogate based on Lowell Observatory's ephemeris API
    def propogate_lowell(self, date, observatory=256):
        ephemera = {
            "observable_asteroids": []
        }

        # Loop through the asteroids
        asteroid_loop = tqdm(self.asteroids, desc="Propogating asteroid positions...", leave=False)
        for asteroid in asteroid_loop:
            mpc = asteroid['minorplanet']['ast_number']
            name = asteroid['minorplanet']['designameByIdDesignationPrimary']['str_designame']
            vmag = asteroid['v_mag']

            if mpc == None:
                mpc = name

            self.url_builder(mpc, observatory, date)
            self.get_results()
            
            eph = self.data['ephemeris']
            coordinates = []

            for i in range(len(eph)):
                ra_deg = eph[i]['ra_deg']
                ra_hms = eph[i]['ra_hms']
                dec_deg = eph[i]['dec_deg']
                dec_dms = eph[i]['dec_dms']
                obs_time = eph[i]['calendar'] 
                coordinates.append({
                    "ra_deg": ra_deg,
                    "dec_deg": dec_deg,
                    "ra_hms": ra_hms,
                    "dec_dms": dec_dms,
                    "obs_time": obs_time
                })
            
            asteroid_data = {
                "mpc": mpc,
                "name": name,
                "vmag": vmag,

                "coordinates": coordinates
            }

            ephemera["observable_asteroids"].append(asteroid_data)
            asteroid_loop.set_description(f"Positions propogated for Asteroid {mpc}. Starting next propogation", refresh=True)
        
        return ephemera

    # Propogate based on coord_rate
    def propogate_rate(self, duration, step, date):
        ephemera = {
            "observable_asteroids": []
        }
        
        try:
            if duration % step != 0:
                raise ValueError("Duration must be divisible by step")
            n_steps = duration // step
                        
            asteroid_loop = tqdm(self.asteroids, desc="Propogating asteroid positions...", leave=False)
            for asteroid in asteroid_loop:
                mpc = asteroid['minorplanet']['ast_number']
                name = asteroid['minorplanet']['designameByIdDesignationPrimary']['str_designame']
                vmag = asteroid['v_mag']

                ra = asteroid['ra']
                ra_rate = asteroid['ra_rate']
                dec = asteroid['dec']
                dec_rate = asteroid['dec_rate']

                ra = ra * 180 / np.pi
                ra_rate = ra_rate/1.74355/60/3600
                dec = dec * 180 / np.pi
                dec_rate = dec_rate/0.4/60/3600

                if mpc == None:
                    mpc = name

                coordinates = []

                coordinates.append({
                    "ra": ra,
                    "dec": dec,
                    "obs_time": date + "T00:00"
                })

                for i in range(n_steps):
                    ra += (ra_rate * step / 15)
                    dec += (dec_rate * step / 15)
                    obs_time = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(minutes=(i+1) * step)
                    obs_time = obs_time.strftime("%Y-%m-%dT%H:%M")

                    coordinates.append({
                        "ra": ra,
                        "dec": dec,
                        "obs_time": obs_time
                    })

                asteroid_data = {
                    "mpc": mpc,
                    "name": name,
                    "vmag": vmag,

                    "coordinates": coordinates
                }

                ephemera["observable_asteroids"].append(asteroid_data)
                asteroid_loop.set_description(f"Positions propogated for Asteroid {mpc}. Starting next propogation", refresh=True)
        
            return ephemera

        except ValueError as e:
            print(f"Error: {e}")
            return 