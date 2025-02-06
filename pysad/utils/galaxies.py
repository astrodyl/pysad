import os
from typing import List, Dict

import pandas
import requests
from pathlib import Path

from pysad.utils.string import sanitize

# DONE: Sort galaxies by probability 

# TODO: Add support for FITs files - GalaxyDB -> FitsDB, CsvDB (?)
# TODO: Sort galaxies by probability after querying, then overwrite file

class GalaxyDB:
    def __init__(self, event: str):
        self.base_url = "https://ned.ipac.caltech.edu/uri/NED::GWFglist/"
        self.event = event
        self.path = None

        self.create()

    def create(self):
        """ Queries the event URL and saves the result to disk.

        :return: list of objects containing galaxy name, ra, and dec
        """
        self.save_to_disk(self.query())

    def query(self, serial_number: str = 'latest') -> requests.models.Response:
        """ Queries the events produced by the NED Gravitational Wave
         Followup (GWF) service.

        :param serial_number: VOEvent Serial number ('1', '2', ..., or 'latest')
        :return: requests.response.status_code
        """
        r = requests.get(f"{self.base_url}/csv/{self.event}/{serial_number}")

        if r.status_code != 200:
            raise RuntimeError(r.text)

        return r

    def get(self, start: int = None, limit: int = None) -> List[Dict]:
        """ Returns a list of objects containing galaxy name, ra (hours),
        and dec (degrees). The number of rows returned is the maximum
        of the provided limit and the number of rows in the file.

        :param start: Starting row to return
        :param limit: number of rows to return
        :return: list of objects containing galaxy name, ra, and dec
        """
        if not os.path.exists(self.path):
            raise ValueError(f"{self.path} does not exist. Did you run 'save_to_disk'?")

        if not self.path.endswith('csv'):
            raise IOError(f"{self.path} is not a CSV file.")

        result = []
        with open(self.path, newline='') as csvfile:
            rows = pandas.read_csv(csvfile, skiprows=start, nrows=limit)

            rows['probability'] = rows['P_3D'] * rows['P_LumW1']
            rows = rows.sort_values(by='probability', ascending=False)

            for row in rows.values:
                result.append({'name': sanitize(str(row[0])), 'ra_hours': row[1] / 15., 'dec_degs': row[2]})

        return result

    def save_to_disk(self, response: requests.Response) -> None:
        """ Writes the Requests.Response object to disk using the specified
        file_format. Allows for overwriting of existing files since the
        user may query the 'latest' version multiple times.

        :param response: Requests.Response object
        """
        event_directory = rf"{Path.cwd()}\\pysad\\results\\{self.event}"
        output_path = f"{event_directory}\\{self.event}.csv"

        if not os.path.exists(event_directory):
            os.mkdir(event_directory)

        with open(output_path, "wb") as file:
            file.write(response.content)

        self.path = output_path
