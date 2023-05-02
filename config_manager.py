import datetime
import json
import os


class ConfigGetter:
    json_path = os.path.join(os.path.dirname(__file__), 'config.json')
    units_path = os.path.join(os.path.dirname(__file__),'units.json')
    config_data_dict = {}
    private_keys = ["START_YEAR", "END_YEAR", "PERIODS_DAYS_AMOUNT", "LOCATION", "TIME_FORMAT", "START_DATE", "END_DATE", "datasource"]

    @classmethod
    def get_locations(cls, d, curr=""):
        res = []
        for key, val in d.items():
            if key not in cls.private_keys:
                if isinstance(val, dict):
                    res += cls.get_locations(val, curr + "-" + key)
                else:
                    res.append(curr + "-" + key)

        return res


    @classmethod
    def load_data(cls):
        with open(cls.json_path) as json_file:
            cls.config_data_dict = json.load(json_file)

        cls.config_data_dict["START_YEAR"] = datetime.datetime.strptime(ConfigGetter["START_DATE"], ConfigGetter["TIME_FORMAT"]).year
        cls.config_data_dict["END_YEAR"] = datetime.datetime.strptime(ConfigGetter["END_DATE"], ConfigGetter["TIME_FORMAT"]).year


    @classmethod
    def __class_getitem__(cls, item):
        return cls.config_data_dict[item]

