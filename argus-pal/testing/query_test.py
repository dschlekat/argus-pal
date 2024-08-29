"""
This script is used to test the Query class in the query.py file.
Outputs the results to the testing/query_test_results.txt file for testing.
"""
import os, sys
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes import Query

# Query Parameters
v_mag_1 = 16      ## limiting magnitude for 1s Pathfinder exposures
date_time = "2024-03-23"
ra_min = 0
ra_max = 150 / 180 * np.pi
dec_min = -20 / 180 * np.pi
dec_max = 70 / 180 * np.pi
limit = 1000

# Builds the query
query = Query()
query.build_query(ra_min, ra_max, dec_min, dec_max, date_time, v_mag_1, limit)
query.get_results()

# Writes the results to a file for testing
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "testing/query_test_results.txt")
with open(file_path, "w") as f:
    f.write("Asteroids visible to Pathfinder on 2024-03-22: \n\n")
    f.write(str(query.response.json()))