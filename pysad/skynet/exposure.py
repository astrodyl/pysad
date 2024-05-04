from pysad.utils import config
from pysad.utils.string import snake_to_camel


class Exposure:
    def __init__(self, telescope: str, section: str = 'Default'):
        self.telescope = telescope
        self.filter_requested = None
        self.exp_length = None
        self.repeat = None
        self.delay = None

        self.from_config(section)

    def from_config(self, section: str) -> None:
        """ Creates an exposure object from the exposures configuration
        file.

        :param section: Exposure config section
        """
        self.set_attributes(section)

    def to_dict(self) -> dict:
        """ Returns a dictionary representation of the exposure. Keys
        are stored in camel case to match the Skynet exposure object
        format.

        :return: Key value pairing of exposure attributes
        """
        return {snake_to_camel(k): v for k, v in vars(self).items() if k not in ['telescope', 'repeat']}

    def set_attributes(self, section: str):
        """ Sets the class attributes based on defined variables in the
        config file.

        :param section: The exposure section config name
        """
        settings = config.read('pysad/config/exposures.ini')

        for attribute, _ in vars(self).items():
            if attribute != 'telescope':
                self.set_attribute(settings, attribute, section)

    def set_attribute(self, settings, attribute: str, section: str, required: bool = True):
        """ Sets the attribute of the requested exposure. Prioritizes
        the telescope section over the section stored in the class as
        a way of allowing specific overrides. If the attribute is
        required but not found, throws a ValueError.

        :param settings: configparser.ConfigParser for exposures
        :param attribute: The attribute to set
        :param required: Whether the attribute is required
        :param section: Exposure section config name
        """
        if value := config.get(settings, self.telescope.upper(), attribute):
            setattr(self, attribute, config.expected_type(value))
        elif value := config.get(settings, section, attribute):
            setattr(self, attribute, config.expected_type(value))
        elif required:
            raise ValueError(f'Exposure config file is missing {attribute} information.')
