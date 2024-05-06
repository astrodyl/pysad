import json

from pysad.actions import schedule
from pysad.skynet import api
from pysad.skynet.observation import Observation
from pysad.utils.galaxies import GalaxyDB


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
    if schedule.is_new_event(kwargs['event']):
        raise RuntimeError(f'The results log for the event {kwargs["event"]}'
                           f' does not exist. Use the "schedule" action instead.')

    with open(f'pysad/results/{kwargs["event"]}/results.json', 'r') as f:
        prev_results = json.load(f)

    galaxies = get_galaxy_list(prev_results, **kwargs)

    # Cancel outdated observations
    outdated = handle_outdated_observations(prev_results, galaxies)

    # Schedule new observations
    results = handle_new_observations(prev_results, galaxies, **kwargs, outdated=outdated)

    log_results(kwargs['event'], prev_results, results, outdated)

    return 0


def get_galaxy_list(results: dict, **kwargs) -> list:
    """

    :param results:
    :param kwargs:
    :return:
    """
    if 'max_obs_per_tele' not in kwargs:
        kwargs['max_obs_per_tele'] = 20

    telescopes = get_event_telescopes(results)

    # Get the most recent list of galaxies for the event
    return GalaxyDB(kwargs['event']).get(start=2, limit=len(telescopes) * kwargs['max_obs_per_tele'])


def get_event_telescopes(results: dict) -> list[str]:
    return list(set([obs['telescope'] for obs in results['observations']]))


# <editor-fold desc="outdated-obs">
def handle_outdated_observations(results: dict[str, dict], galaxies: list[dict]) -> dict:
    """

    :param results:
    :param galaxies:
    :return:
    """
    outdated = get_outdated_observations(results, galaxies)

    for _, value in outdated.items():
        cancel_outdated_observations(value)

    return outdated


def get_outdated_observations(results: dict, galaxies: list[dict]):
    """

    :param results:
    :param galaxies:
    :return:
    """
    desired_galaxies = [g['name'] for g in galaxies]

    outdated = {}
    for obs in results['observations']:
        if obs['name'] not in desired_galaxies:
            if obs['telescope'] in outdated:
                outdated[obs['telescope']].append(obs['id'])
            else:
                outdated[obs['telescope']] = [obs['id']]

    return outdated


def cancel_outdated_observations(obs_ids: list):
    """

    :param obs_ids:
    :return:
    """
    for obs_id in obs_ids:
        api.update_observation(id=obs_id, state='canceled')
# </editor-fold>"


# <editor-fold desc="new-obs">
def handle_new_observations(results: dict, galaxies: list[dict], **kwargs) -> dict:
    """

    :param results:
    :param galaxies:
    :return:
    """
    requests = get_new_observations(results, galaxies, **kwargs)
    return schedule.submit_obs_requests(requests)


def get_new_observations(results: dict, galaxies: list[dict], **kwargs) -> list[dict]:
    """

    :param results:
    :param galaxies:
    :return:
    """
    tele_queue_space = kwargs['outdated']

    observed_galaxies = [obs['name'] for obs in results['observations']]
    new_galaxies = [g for g in galaxies if g['name'] not in observed_galaxies]

    obs_requests, index = [], 0
    for tele in tele_queue_space:
        for _ in range(len(tele_queue_space[tele])):
            if index < len(new_galaxies):
                obs = Observation(tele, new_galaxies[index], kwargs['obs_section'], kwargs['exp_section'])
                obs_requests.append(obs.to_dict())
                index += 1
            else:
                break  # Out of galaxies to observe

    return obs_requests
# </editor-fold>


def log_results(event: str, results: dict, added: dict, outdated: dict) -> int:
    """ Writes the results dictionary to 'gwsad/results/<event>/results.json'.

    :param event: event name
    :param results: previous results
    :param added: dictionary of new results
    :param outdated: dict of canceled observations
    :return: 0 for success
    """
    canceled_obs_ids = []
    for _, obs_ids in outdated.items():
        canceled_obs_ids.extend(obs_ids)

    # Remove canceled observations
    obs_to_remove = []
    for obs in results['observations']:
        if obs['id'] in canceled_obs_ids:
            obs_to_remove.append(obs)

    results['observations'] = [obs for obs in results['observations'] if obs not in obs_to_remove]

    # Add new observations
    results['observations'].extend(added['observations'])

    with open(f'pysad/results/{event}/results.json', 'w') as f:
        f.write(json.dumps(results, indent=4))

    return 0
