"""
Contains the Query class, which is used to build and post queries to the astorbdb GraphQL API.
Has the functions:
    __init__(): Initializes the Query object with the API url.
    build_query(): Builds the query based on the inputs.
    get_results(): Posts the query and returns the results.
"""
import requests
import time

class Query():
    url = None
    query = None
    response = None
    data = None


    def __init__(self):
        # Init function, sets the url for the query
        self.url = 'https://astorbdb.lowell.edu/v1/graphql'
    

    # Builds the query based on the inputs
    def build_query(self, ra_min, ra_max, dec_min, dec_max, date, mag_lim, limit):
        # Creates the GraphQL query within a Python string      
        self.query = f"""query ExampleQuery {{
            ephemeris(
                where: {{
                eph_date: {{_eq: "{date}"}},
                ra:       {{_gte: "{ra_min}", _lte: "{ra_max}"}}, 
                dec:      {{_gte: "{dec_min}", _lte: "{dec_max}"}},
                v_mag:    {{_lte: "{mag_lim}"}}
                }}
                order_by: {{id_minorplanet: asc}}
                limit: {limit}
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
