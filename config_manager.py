import json
import os


class ConfigGetter:
    json_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config_data_dict = {}

    @classmethod
    def load_data(cls):
        with open(cls.json_path) as json_file:
            cls.config_data_dict = json.load(json_file)

    @classmethod
    def __class_getitem__(cls, item):
        return cls.config_data_dict[item]

