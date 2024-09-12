# Argus PAL
This is an in-progress script that generates detailed ephemera for asteroids visible to the Argus Pathfinder instrument ([https://evryscope.astro.unc.edu/2022/12/06/argus-pathfinder-deployed-to-pari/](url), Vasquez et al. 2024) each night. The Argus Pathfinder is a multi-camera, wide-field instrument capable of high-cadence surveys of the night sky. This project was originally started for the class ASTR 502: Modern Research in Astrophysics at UNC-Chapel Hill during the spring semester of 2024. Eventually, the PAL will be able to return an ephemera for any on-sky location over any set period of time.

The tool uses the Lowell Observatory's Astorb database to query for
asteroids that are visible in the sky at the time of observation, 
as well as the Astropy library for various astronomical calculations.

## Use
**Note:** to run each of the files create a virtual environment and install the required packages (with pip) using the following commands:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Before running the script, update the `__main__.py` file with the desired date of observation. The script will then return a list of asteroids visible to the Argus Pathfinder instrument at that date, along with their apparent magnitude and positions throughout the night.

To run the script, simply run the following command in the terminal:
```
python3 -m pal
```

## Attribution
This code can be used freely as long as the user attributes credit to the author (Donovan Schlekat).

## Acknowledgements
This project was made possible by the guidance of Dr. Nicholas Law and graduate students Shannon Fitton, Lawrence Machia, and Will Marshall. The author would also like to thank the Lowell Observatory for providing the Astorb database for public use. 
