# ASTR502: Target Finding Group
# Finding asteroids observable by Pathfinder

## Task overview
To determine which asteroids are observable, and locate them within Pathfinder images, we needed to create a program capable of querying their ephemeris database from an external database.
The program had to be able to query the database for a certain right ascension (RA) range based on the date of observation (which affects the sidereal time), a declination (Dec) range based on Pathfinder's field-of-view (FoV), and the date of observation.
The program had to be able to take input dates to query.

## Task plan
  - Generate a list of dates for observation
  - Create an object to query the Lowell Asteroid Ephemeris database based on input parameters
  - Create an object to read a list of dates and determine the observable RA range for each date
  - Create a pipeline that takes in an input date, or list of dates, and queries the database, writing the responses to .txt files in JSON format.

## Task results
**Note:** to run each of the files, one must have activated a Python environment containing the dependency packages imported in pipeline.py, query.py, and import.py.
An actual requirements.txt file and instructions on installing these dependencies into a virtual environment will be written eventually.
All instructions for running the programs in a command-line interface assume that the user has changed directories into pathfinder_targets.
This can be done (when originally located in astr502_spring2024) by running `cd target_finding/graphQL_queries/pathfinder_targets`.

The following are files/folders contained within the pathfinder_targets folder:
 
  - **datemaker.py**
     - Creates a .txt file with dates from the date the program is run until the final day of the semester (May 10th).
       - Resulting file path: `astr502_spring2024/target_finding/graphQL_queries/pathfinder_targets/data/all_dates_PF.txt`
     - Run in the command line as `python datemaker.py`
       - (Note: you may need to specify the Python version: `python3 datemaker.py`)
 
  - **inputs.py**
     - Code for the Input object that takes dates and returns right ascension FoV fields.
     - The Input object contains two primary methods:
       - `Input.get_dates()`: Takes a file path, parses each line as a date, and returns a list of dates as strings in YYYY-MM-DD format.
         - Input:
           - `file_path` (str, path to .txt file with dates)
         - Output:
           - `Input.dates` (list[str], list of dates as strings in YYYY-MM-DD format)
       - `Input.get_ra_range()`: Takes a date as a string in YYYY-MM-DD format and returns Pathfinder's observable RA range for that night.
         - Input:
           - `date` (str, YYYY-MM-DD format)
         - Output (returned):
           - `ra_min` (float, minimum right ascension in decimal degrees)
           - `ra_max` (float, maximum right ascension in decimal degrees)
         - Note: the date refers to the day of the morning of the observation. So if the date is 2024-04-04, the observable RA range is for the night starting on 04-03 and ending on 04-04.
 
  - **query.py**
     - Code for the Query object that takes query parameters and returns ephemeris data for all asteroids within the desired FoV and on the desired date.
     - The query uses the Lowell Observatory astorbDB API (docs: [https://asteroid.lowell.edu/docs/graphql/](url); endpoint: [https://astorbdb.lowell.edu/v1/graphql](url))
     - The Query object contains two primary methods:
       - `Query.build_query()`: Takes in query parameters and builds the corresponding GraphQL query as a Python string.
         - Input:
           - `ra_min` (minimum right ascension in radians)
           - `ra_max` (maximum right ascension in radians)
           - `dec_min` (minimum declination in radians)
           - `dec_max` (maximum declination in radians)
           - `date` (str, date of observation in YYYY-MM-DD format)
           - `mag_lim` (int, upper magnitude limit of observing instrument)
           - `limit` (int, maximum number of objects to respond with)
         - Output:
           - `Query.query` (GraphQL query as a Python string)
       - `Query.get_results()`: Uses a pre-made query to access the astorbDB API, waits for a positive, non-empty result, and returns.
         - This function will access the API repeatedly up to a set amount of retry attempts if the query fails.
         - Input:
           - `Query.query` (GraphQL query as a Python string)
           - `max_retries` (maximum amount of retries if the API times out. Default = 5)
         - Output:
           - `Query.response` (astorbDB API response object)
             - Can be decoded as a JSON object using `Query.response.json()`
             - Contains a status code, accessed using `Query.response.status_code`
               - 200: positive, normal response
               - 504: Time-out error
                
  - **pipeline.py**
     - Script that runs the targeting pipeline for finding asteroids observable by Pathfinder on specified dates using the Input and Query objects.
     - Run in the command line as `python pipeline.py`, user will be prompted to provide inputs (commands in parentheses).
       - (Note: you may need to specify the Python version: `python3 datemaker.py`)
     - Input:
       - (`0`) Text input: 
         - (`{file path}`) Reads input dates from a text file.
         - (`d`) Uses the default dates set in `data/all_dates_PF.txt`
       - (`1`) Manual input:
         - (`{date}`) Takes an input date in YYYY-MM-DD format.
         - (`t`) Uses the execution date of the script as the default date.
     -  Output:
         -  For every input date, the pipeline writes the ephemeris data for the observable asteroids to a .txt file at the path `data/eph_{date}.txt`. The contained data is listed in JSON format. Each asteroid object contains the following parameters:
            - "minorplanet": an object containing administrative information about the asteroid. Contains the following:
              - "ast_number": the asteroid's MPC number.
              - "designameByIdDesignationPrimary": "str_designame": the asteroid's name, if applicable.
            - "ra": The right ascension of the asteroid at 0 UTC on the queried date, in radians.
            - "ra_rate": The on-sky movement rate of the asteroid's right ascension, units unknown.
            - "dec": The declination of the asteroid at 0 UTC on the queried date, in radians.
            - "dec_rate": The on-sky movement rate of the asteroid's right ascension, units unknown.
            - "v_mag": The visible magnitude of the asteroid from Earth on the queried date.

