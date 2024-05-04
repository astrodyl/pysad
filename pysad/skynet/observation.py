from typing import List, Dict

from pysad.skynet.exposure import Exposure
from pysad.utils import config, custom
from pysad.utils.string import snake_to_camel


class Observation:
    def __init__(self, telescope: str, galaxy: Dict = None, section: str = 'Default', exp_section: str = 'Default'):
        self.name = galaxy['name'] if galaxy else None

        # Coordinates
        self.ra_hours = galaxy['ra_hours'] if galaxy else None
        self.dec_degs = galaxy['dec_degs'] if galaxy else None

        # Target Of Opportunity
        self.is_too = None
        self.too_justification = None

        # Observing Constraints
        self.min_el = None
        self.max_sun = None
        self.min_moon_sep_degs = None

        # Miscellaneous
        self.efficiency = None
        self.object_type = None
        self.target_tracking = None
        self.time_account_id = None
        self.telescopes = telescope

        self.exps: List = []

        self.from_config(telescope, section, exp_section)

    def from_config(self, telescope: str, section: str, exp_section: str) -> None:
        """ Creates an observation object from the observation
         configuration file and telescope name.

        :param telescope: Telescope name
        :param section: Observation section config name
        :param exp_section: Exposure section config name
        """
        self.set_attributes(section)
        self.add_exposures(telescope, exp_section)

    def to_dict(self) -> dict:
        """ Returns a dictionary representation of the observation. Keys
        are stored in camel case to match the Skynet observation object
        format.

        :return: Key value pairing of observation attributes
        """
        return {snake_to_camel(k): v for k, v in vars(self).items()}

    def set_attributes(self, section: str) -> None:
        """ Sets the length of the requested exposure. Throws a ValueError
        exception if the key is not present.

        :param section: Observation config option
        """
        exclude = ['exps', 'name', 'ra_hours', 'dec_degs', 'telescopes']
        settings = config.read('pysad/config/observation.ini')

        for attribute, _ in vars(self).items():
            if attribute not in exclude:
                self.set_attribute(settings, attribute, section)

    def set_attribute(self, settings, attribute: str, section: str = 'Default', required: bool = True) -> None:
        """ Sets the attribute of the requested observation. If the attribute
        is required but not found, throws a ValueError.

        :param settings: configparser.ConfigParser for observation
        :param attribute: The attribute to set
        :param section: The observation config section
        :param required: Whether the attribute is required
        """
        if value := config.get(settings, section, attribute):
            setattr(self, attribute, config.expected_type(value))
        elif required:
            raise ValueError(f'Observation config file is missing {attribute} information.')

    def set_coordinates(self, ra_hours: float, dec_degs: float) -> None:
        """ Sets the coordinates of the requested observation.

        :param ra_hours: Right ascension in hours: 0 to 24
        :param dec_degs: Declination in degrees: -90 to 90
        """
        self.ra_hours = ra_hours
        self.dec_degs = dec_degs

    def add_exposures(self, telescope: str, section: str = 'Default') -> None:
        """ Creates a list of exposure requests for the observation.

        :param telescope: The telescope name
        :param section: The exposure config section name
        """
        # Handle custom config sections
        if section == '.DynamicMoon':
            section = custom.dynamic_moon(self.ra_hours, self.dec_degs)

        exp = Exposure(telescope, section)

        for i in range(0, exp.repeat):
            self.exps.append({
                'expLength': exp.exp_length,
                'filterRequested': exp.filter_requested,
                'delay': exp.delay if i != 0 else None
            })
