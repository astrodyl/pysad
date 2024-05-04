import json
import logging
from typing import Dict, List

from pysad.skynet import api
from pysad.skynet.observation import Observation
from pysad.utils.galaxies import GalaxyDB
from pysad.utils import config


def execute(**kwargs) -> int:
    """ Creates an observation request for each galaxy and submits
    each request to the Skynet API to begin observing.

    :param kwargs: Accepted keyword arguments include:
        :Required:
            - event (str): event name
            - obs_section (str): observation section config name
            - exp_section (str): observation section config name
            - tel_section {str}: telescope section config name
        :Optional:
            - max_obs_per_tele (int): max num of obs per telescope

    :return: status code
    """
    obs_requests = create_obs_requests(**kwargs)
    results = submit_obs_requests(obs_requests)

    return log_results(kwargs['event'], results)


def create_obs_requests(**kwargs) -> List[Dict]:
    """ Creates a serializable dictionary for each observation object
    that can be submitted via the Skynet API.

    :param kwargs: Accepted keyword arguments include:
        :Required:
            - event (str): event name
            - obs_section (str): observation section config name
            - exp_section (str): observation section config name
            - tel_section {str}: telescope section config name
        :Optional:
            - max_obs_per_tele (int): max num of obs per telescope

    :return: list of dictionary observation requests
    """
    try:
        galaxies_per_telescope = kwargs['max_obs_per_tele']
    except KeyError:
        galaxies_per_telescope = 20

    # Telescopes used for the observations
    telescopes = get_telescope_list(kwargs['tel_section'])

    # Gets the exact amount of galaxies based on the number of provided telescopes
    galaxies = GalaxyDB(kwargs['event']).get(limit=len(telescopes) * galaxies_per_telescope)

    obs_requests, index = [], 0
    for telescope in telescopes:
        for _ in range(galaxies_per_telescope):
            if index < len(galaxies):
                obs = Observation(telescope, galaxies[index], kwargs['obs_section'], kwargs['exp_section'])
                obs_requests.append(obs.to_dict())
                index += 1
            else:
                break  # Out of galaxies to observe

    return obs_requests


def submit_obs_requests(requests: List[Dict]) -> Dict:
    """ Submits the observation requests to the Skynet API.

    :param requests: List of observation requests
    :return:
    """
    results = {}

    for request in requests:
        try:
            obs = api.add_observation(exps=json.dumps(request.pop('exps')), **request)
        except RuntimeError as e:
            logging.exception(e)
        else:
            results[obs['name']] = {'id': obs['id'], 'telescope': request['telescopes']}

    return results


def get_telescope_list(telescope_section: str) -> list[str | None] | str | None:
    """ Returns a list of all telescope names in the provided telescope
    config option.

    :param telescope_section: Telescope config option
    :return: List of telescope names
    """
    settings = config.read('pysad/config/telescopes.ini')

    telescopes = config.get(settings, telescope_section, 'telescopes')
    telescopes = config.expected_type(telescopes)

    if isinstance(telescopes, str):
        return [telescopes]

    if isinstance(telescopes, list):
        return telescopes


def log_results(event: str, results: Dict) -> int:
    """ Writes the results dictionary to 'gwsad/results/<event>/results.json'.

    :param event: Event name
    :param results: Dictionary of results
    :return: 0 for success
    """
    with open(f'pysad/results/{event}/results.json', 'w') as f:
        f.write(json.dumps(results, indent=4))

    return 0
