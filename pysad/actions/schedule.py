import json
import logging
import os

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
    if not is_new_event(kwargs['event']):
        raise RuntimeError(f'{kwargs["event"]} is already being managed. '
                           f'Use the "update" action instead.')

    obs_requests = create_obs_requests(**kwargs)
    results = submit_obs_requests(obs_requests)

    return log_results(kwargs['event'], results)


def is_new_event(event: str) -> bool:
    """ Checks if there is a results file for the provided event. If
    there is no results file, the event is considered new.

    :param event: event name
    :return: True if event is new, False otherwise
    """
    return not os.path.exists(f'pysad/results/{event}/results.json')


def create_obs_requests(**kwargs) -> list[dict]:
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
            - galaxies (dict): name, ra, dec for each galaxy

    :return: list of dictionary observation requests
    """
    kwargs = check_kwargs(**kwargs)

    obs_requests, index = [], 0
    for telescope in kwargs['telescopes']:
        for _ in range(kwargs['max_obs_per_tele']):
            if index < len(kwargs['galaxies']):
                obs = Observation(telescope=telescope,
                                  galaxy=kwargs['galaxies'][index],
                                  section=kwargs['obs_section'],
                                  exp_section=kwargs['exp_section'])
                obs_requests.append(obs.to_dict())
                index += 1
            else:
                break  # Out of galaxies to observe

    return obs_requests


def submit_obs_requests(requests: list[dict]) -> dict:
    """ Submits the observation requests to the Skynet API.

    :param requests: List of observation requests
    :return:
    """
    results = {'observations': []}

    for request in requests:
        try:
            obs = api.add_observation(exps=json.dumps(request.pop('exps')), **request)
        except RuntimeError as e:
            logging.exception(e)
        else:
            results['observations'].append({
                'id': obs['id'],
                'state': 'active',
                'name': obs['name'],
                'telescope': request['telescopes']}
            )

    return results


def get_telescopes(telescope_section: str) -> list[str | None] | str | None:
    """ Returns a list of all telescope names in the provided telescope
    config option.

    :param telescope_section: Telescope config option
    :return: List of telescope names
    """
    settings = config.read('pysad/config/telescopes.ini')

    telescopes = config.get(settings, telescope_section, 'telescopes')
    telescopes = config.expected_type(telescopes)

    return telescopes if isinstance(telescopes, list) else [telescopes]


def check_kwargs(**kwargs):
    """ Checks for optional keyword arguments and populates them if they
    are not provided.

    :param kwargs: Accepted keyword arguments include:
        - max_obs_per_tele (int): max num of obs per telescope
        - galaxies (dict): name, ra, dec for each galaxy
    :return: dictionary with optional params defined
    """
    if 'max_obs_per_tele' not in kwargs:
        kwargs['max_obs_per_tele'] = 20

    if 'telescopes' not in kwargs:
        kwargs['telescopes'] = get_telescopes(kwargs['tel_section'])

    if 'galaxies' not in kwargs:
        limit = len(kwargs['telescopes']) * kwargs['max_obs_per_tele']
        kwargs['galaxies'] = GalaxyDB(kwargs['event']).get(limit=limit)

    return kwargs


def log_results(event: str, results: dict) -> int:
    """ Writes the results dictionary to 'gwsad/results/<event>/results.json'.

    :param event: Event name
    :param results: Dictionary of results
    :return: 0 for success
    """
    with open(f'pysad/results/{event}/results.json', 'w') as f:
        f.write(json.dumps(results, indent=4))

    return 0
