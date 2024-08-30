import requests
import time

"""
    Contains the Query class, which is used to build and post queries to the AstorbDB GraphQL API.
    Has the functions:
        __init__(): Initializes the Query object with the API url.
        build_query(): Builds the query based on the inputs.
        get_results(): Posts the query and stores the results in the query object.
"""

class Query():
    url = None
    query = None
    response = None
    data = None


    def __init__(self):
        """ Initializes the Query object with the API url."""
        self.url = 'https://astorbdb.lowell.edu/v1/graphql'
    

    # Builds the query based on the inputs
    def build_query(self, ra_min, ra_max, dec_min, dec_max, date, mag_lim, last_id=None):
        """ Builds the GraphQL query based on the inputs.
        :param ra_min: The minimum right ascension.
        :param ra_max: The maximum right ascension.
        :param dec_min: The minimum declination.
        :param dec_max: The maximum declination.
        :param date: The date of the observation.
        :param mag_lim: The magnitude limit.
        :param last_id: The last asteroid id to continue the query
        """   
        self.query = f"""query ExampleQuery {{
            ephemeris(
                where: {{
                eph_date: {{_eq: "{date}"}},
                ra:       {{_gte: "{ra_min}", _lte: "{ra_max}"}}, 
                dec:      {{_gte: "{dec_min}", _lte: "{dec_max}"}},
                v_mag:    {{_lte: "{mag_lim}"}}
                {f', id_minorplanet: {{_gt: "{last_id}"}}' if last_id else ''}
                }}
                order_by: {{id_minorplanet: asc}}
            ) {{
                minorplanet {{
                ast_number
                designameByIdDesignationPrimary {{
                    str_designame
                }}
                }}
                ra
                ra_rate
                dec
                dec_rate
                v_mag
            }}
        }}"""
    

    # Posts the query and returns the results
    def get_results(self, max_retries=5):
        """ Posts the query and stores the results in the query object.
        :param max_retries: The maximum number of retries for the query.
        """
        retry_count = 0
        try:
            # Retry the request if it fails
            while retry_count < max_retries:
                # Post the query
                self.response = requests.post(
                    "https://astorbdb.lowell.edu/v1/graphql",
                    json={"query": self.query},
                )

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
                else:
                    print(f"Request failed with status code: ", self.response.status_code)

                retry_count += 1
                time.sleep(1 + retry_count)  # Wait for 1+ seconds before retrying, to not overwhelm the server
        except Exception as e:
            raise IOError("Error posting query: {e}")
