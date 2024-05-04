import requests

from pysad.utils import config


def get_base_url(settings) -> str:
    """ Returns the base URL for a Skynet API request.

    :param settings: configparser.ConfigParser
    :return: Server URL with API version
    """
    return f'{get_api_server(settings)}/{get_api_version(settings)}'


def get_api_server(settings):
    """ Returns the base URL for a Skynet API request.

    :param settings: configparser.ConfigParser
    :return: Server URL
    """
    return settings.get('API', 'server')


def get_api_key(settings) -> str:
    """ Returns the API key for a Skynet API request.

    :param settings: configparser.ConfigParser
    :return: API key
    """
    return settings.get('API', 'token')


def get_api_version(settings) -> str:
    """ Returns the API version for a Skynet API request.

    :param settings: configparser.ConfigParser
    :return: API version
    """
    return settings.get('API', 'version')


def handle_server_response(r: requests.models.Response):
    """ Handles a successful server response from Skynet API and returns
    the appropriate object(s).

    :param r: requests.models.Response
    :return: Tuple of (filename, data) or deserialized json object
    """
    if r.status_code != 200:
        raise RuntimeError(r.text)

    try:
        # Retrieve the filename if request was a download request
        try:
            filename = r.headers['Content-Disposition'].split('attachment; filename=', 1)[1]
        except IndexError:
            filename = r.headers['Content-Disposition'].split('inline; filename=', 1)[1]

    # Return the deserialized object
    except (KeyError, IndexError):
        if r.headers['Content-Type'] == 'text/plain':
            return r.text
        return r.json()

    # Return the filename and raw data
    else:
        return filename[filename.index('"') + 1:filename.rindex('"')].strip(), r.content


def add_observation(**kwargs):
    """ Submits a request to the Skynet API to add an observation.
    If the request is unsuccessful due to a missing rprime filter,
    reattempts with the R filter. Throws a RuntimeError if the
    request is still unsuccessful.

    :param kwargs: Dictionary of request parameters
    :return: Dictionary matching Skynet ObservationSchema
    """
    settings = config.read('pysad/config/api.ini')
    request = {'data': kwargs, 'headers': {'Authentication-Token': get_api_key(settings)}}

    r = requests.request('POST', f'{get_base_url(settings)}/obs', **request)

    if r.status_code != 200:
        if 'has no filter "rprime"' in r.text:
            kwargs['exps'] = kwargs['exps'].replace('"rprime"', '"R"')
            return add_observation(**kwargs)
        else:
            raise RuntimeError(r.text)

    return handle_server_response(r)


def update_observation(**kwargs):
    """ Updates the parameters of a Skynet Observation.

    :param kwargs: Accepted keyword arguments include:
        :Required:
            - id (int | str): Observation ID
        :Optional:
            - Any Skynet ObservationSchema field/value to modify

    :return: Dictionary matching Skynet ObservationSchema
    """
    obs_id = int(kwargs.pop('id'))

    settings = config.read('pysad/config/api.ini')
    request = {'data': kwargs, 'headers': {'Authentication-Token': get_api_key(settings)}}

    r = requests.request('PUT', f'{get_base_url(settings)}/obs/{obs_id}', **request)

    if r.status_code != 200:
        raise RuntimeError(r.text)

    return handle_server_response(r)
