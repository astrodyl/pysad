import sys

from pysad.actions import schedule, update, cancel

"""
    Gravitational Wave Search And Discovery (GWSAD)
    
    GWSAD is a Python tool that utilizes the Skynet Robotic Telescope
    Network's (https://skynet.unc.edu/) public API to perform a narrow 
    field, targeted search and discovery across the LIGO Virgo Collaboration
    (LVC) localization region.

    This tool also makes use of the NASA/IPAC Extragalactic Database (NED). 
    See: https://ned.ipac.caltech.edu/Documents/Overview.
"""


# DONE: Allow for substitute filters. E.g., if no rprime, use r
# DONE: Allow for custom config settings: E.g., DynamicMoon
# DONE: pip freeze > requirements.txt
# DONE: Implement cancelling observations

# TODO: Allow union of telescopes. E.g., Northern | NonDLT100
# TODO: Group galaxies by proximity to reduce slewing time
# TODO: Implement dynamic observation limit per telescope based on exp length


def execute(**kwargs) -> int:
    """ Executes the given action on the given event.

    :param kwargs: Accepted keyword arguments include:
        :Required:
            - event (str): event name
            - obs_section (str): observation section config name
            - exp_section (str): exposure section config name
            - tel_section {str}: telescope section config name
        :Optional:
            - max_obs_per_tele (int): max num of obs per telescope

    :return: exit status code
    """
    action = kwargs.pop('action')

    if action.lower() == 'schedule':
        return schedule.execute(**kwargs)
    if action.lower() == 'update':
        return update.execute(**kwargs)
    if action.lower() == 'cancel':
        return cancel.execute(**kwargs)

    raise ValueError('Invalid action provided. Supported actions '
                     'include: schedule, update, cancel.')


def main(p: dict) -> int:
    return execute(**p)


if __name__ == '__main__':

    params = {

        # Required
        'event': 'GW170817',       # GW event name; e.g., s240414ed
        'action': 'cancel',        # One of schedule, update, or cancel
        'obs_section': 'Default',  # Observation configuration section
        'exp_section': 'Default',  # Exposure configuration section
        'tel_section': 'Default',  # Telescopes configuration section

        # Optional
        'max_obs_per_tele': 1      # Max number of galaxies per telescope

    }

    sys.exit(main(params))
