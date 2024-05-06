import json
import logging

from pysad.skynet import api


def execute(**kwargs) -> int:
    """ Cancels Skynet observations for the provided event by sending
    an update request via the Skynet API.

    :param kwargs: Accepted keyword arguments include:
        :Required:
            - event (str): event name

    :return: status code
    """
    with open(f'pysad/results/{kwargs["event"]}/results.json', 'r') as f:
        results = json.load(f)

    for obs in results['observations']:
        try:
            api.update_observation(**{'id': obs['id'], 'state': 'canceled'})
        except RuntimeError as e:
            logging.exception(e)

    return 0
