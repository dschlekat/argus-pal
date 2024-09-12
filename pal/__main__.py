import sys
from importlib import import_module

"""
    Argus Pathfinder Asteroid Locator (Argus-PAL)

    Argus-PAL is a tool that allows users to locate asteroids within 
    Argus Pathfinder images. The Argus Pathfinder is a telescope located
    at the Pisgah Astronomical Research Institute (PARI) in Rosman, NC.
    The telescope, a prototype for the Argus Array, is a wide-field, 
    high-cadence optical telescope useful for observing transient events
    and, as shown with this tool, asteroids.

    The tool uses the Lowell Observatory's Astorb database to query for
    asteroids that are visible in the sky at the time of observation, 
    as well as the Astropy library for various astronomical calculations.

    The tool is designed to be run from the command line, and requires
    a configuration file to be passed in as an argument. The configuration
    file should contain the necessary information for the telescope.
"""

# DONE: Implement the asteroid class for type hinting
# DONE: Implement query code in pipeline.py
# DONE: Implement logging code in ephemeris.py and logging.py
# DONE: Fix query retrying when max asteroids is reached

# TODO: Implement propogate code in propogate.py

def exectute(**kwargs) -> int:
    """ Execute the Argus-PAL tool with the given parameters.

    :param kwargs: Accepted parameters for the tool:
            - action: The action to perform. Currently only 'ephemeris' is supported.
            - telescope: The name of the telescope to use. Check the configuration file for available telescopes.
            - start_date: The start date for the observation period.
            - end_date: The end date for the observation period.
            - mag_lim: Whether to apply a magnitude limit to the query. Default is False. If set to True, the tool will only return asteroids with a magnitude less than or equal to the limit, which is set by the telescope.
            - propogation_interval: The interval at which to propogate the asteroid locations throughout the night. Default is 15 minutes.
    :return: 0 if successful, 1 if an error occurred.
    """
    return import_module(f'pal.actions.{kwargs.pop("action")}').execute(**kwargs)

def main(p: dict) -> int:
    return exectute(**p)

if __name__ == "__main__":
    
    params = {

        # required
        "action": "ephemeris",
        "telescope": "Pathfinder",
        "start_date": "2025-01-08",
        "end_date": "2025-01-15",
        "mag_lim": True,
        "propogation_interval": 15,

    }

    try:
        sys.exit(main(params))
    except KeyboardInterrupt:
        print("\n")
        print("Keyboard interrupt activated. Quitting...")
        sys.exit(1)