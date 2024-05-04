import math
from datetime import datetime

import ephem

from pysad.utils import config

"""
    Custom Configuration
    
    The Custom Configuration Library is a centralized collection of
    methods to handle custom configuration settings. To define a custom
    configuration, the section name in the .ini file must start with
    a period.
"""


def dynamic_moon(target_ra: float, target_dec: float) -> str:
    """ Determines the phase of the moon and proximity of the target to
    the moon and returns which moon exposure configuration to use.

    Makes use of PyEphem Astronomy Library: https://rhodesmill.org/pyephem/

    :param target_ra: Right ascension in hours
    :param target_dec: declination in degrees
    :return: 'BrightMoon' or 'DarkMoon'
    """
    settings = config.read('pysad/config/exposures.ini')

    max_phase = config.get(settings, '.DynamicMoon', 'max_phase')
    min_sep_degs = config.get(settings, '.DynamicMoon', 'min_sep_degs')

    # Get the moon ra, dec, and phase
    moon = ephem.Moon()
    moon.compute(datetime.utcnow())

    if moon.phase < config.expected_type(max_phase):
        return 'DarkMoon'

    # Determine the separation of the target and moon
    sep_ra_rads = math.radians(math.fabs(target_ra - moon.ra))
    sep_dec_rads = math.radians(math.fabs(target_dec - moon.dec))

    separation = math.pow(math.sin(sep_dec_rads / 2.0), 2.0)
    separation += (math.cos(math.radians(moon.dec)) *
                   math.cos(math.radians(target_dec)) *
                   math.pow(math.sin(sep_ra_rads / 2.0), 2.0))
    separation = math.degrees(2.0 * math.asin(math.sqrt(separation)))

    if separation >= config.expected_type(min_sep_degs):
        return 'DarkMoon'

    return 'BrightMoon'
