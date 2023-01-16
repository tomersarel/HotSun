import datetime
import json
import os


class ConfigGetter:
    json_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config_data_dict = {}

    @classmethod
    def load_data(cls):
        with open(cls.json_path) as json_file:
            cls.config_data_dict = json.load(json_file)

        cls.config_data_dict["START_YEAR"] = datetime.datetime.strptime(ConfigGetter["START_DATE"], ConfigGetter["TIME_FORMAT"]).year
        cls.config_data_dict["END_YEAR"] = datetime.datetime.strptime(ConfigGetter["END_DATE"], ConfigGetter["TIME_FORMAT"]).year

    @classmethod
    def __class_getitem__(cls, item):
        return cls.config_data_dict[item]
