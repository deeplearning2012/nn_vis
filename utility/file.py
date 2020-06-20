import json
import os
from functools import reduce
from typing import Dict, List
from datetime import datetime, timezone

from definitions import BASE_PATH
from utility.singleton import Singleton


class FileHandler(metaclass=Singleton):
    def __init__(self):
        self.storage_path: str = os.path.join(BASE_PATH, 'storage')
        self.stats_cache: Dict[str, Dict[str, any]] = dict()
        self.day_key: str = datetime.utcfromtimestamp(
            datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())).strftime(
            '%Y-%m-%d')
        os.makedirs("%s/stats" % self.storage_path, exist_ok=True)

    def read_statistics(self):
        try:
            with open("%s/stats/%s.json" % (self.storage_path, self.day_key), "r") as stats_file:
                file_data = stats_file.read()
                if file_data:
                    self.stats_cache = json.loads(file_data)
                    for name, stat in self.stats_cache.items():
                        for time, time_stat_slice in stat.items():
                            if type(time_stat_slice) is not "list":
                                self.stats_cache[name][time] = [time_stat_slice]
        except FileNotFoundError:
            with open("%s/stats/%s.json" % (self.storage_path, self.day_key), 'w+'):
                pass

    def append_statistics(self, data: Dict[str, any]):
        time_key: str = datetime.utcfromtimestamp(
            datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())).strftime(
            '%Y-%m-%d %H:%M:%S')

        for name, stat in data.items():
            if name not in self.stats_cache.keys():
                self.stats_cache[name] = dict()
            if time_key not in self.stats_cache[name].keys():
                self.stats_cache[name][time_key] = []
            self.stats_cache[name][time_key].append(stat)

    def write_statistics(self):
        for name, stat in self.stats_cache.items():
            for time, time_stat_slice in stat.items():
                if len(time_stat_slice) is 1:
                    self.stats_cache[name][time] = time_stat_slice[0]
                else:
                    self.stats_cache[name][time] = reduce(lambda a, b: a + b, time_stat_slice) / len(time_stat_slice)

        with open("%s/stats/%s.json" % (self.storage_path, self.day_key), "w") as stats_file:
            stats_file.write(json.dumps(self.stats_cache))


class EvaluationFile:
    def __init__(self, name: str):
        self.directory_path: str = os.path.join(BASE_PATH, os.path.join('storage', 'evaluation'))
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)
        self.name = name

        self.data_cache: Dict[str, Dict[str, Dict[any, any]]] = dict()
        self.day_key: str = datetime.utcfromtimestamp(
            datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())).strftime(
            '%Y-%m-%d')

    def read_data(self):
        try:
            with open("%s/%s_%s.json" % (self.directory_path, self.name, self.day_key), "r") as stats_file:
                file_data = stats_file.read()
                if file_data:
                    self.data_cache = json.loads(file_data)
        except FileNotFoundError:
            with open("%s/%s_%s.json" % (self.directory_path, self.name, self.day_key), 'w+'):
                pass

    def append_main_data(self, key: str, sub_key: str, data: Dict[any, any]):
        if key not in self.data_cache.keys():
            self.data_cache[key] = dict()
        if sub_key not in self.data_cache[key].keys():
            self.data_cache[key][sub_key] = data
        else:
            self.data_cache[key][sub_key].update(data)

    def append_data(self, key: str, sub_key: str, sub_sub_key: str, data: Dict[any, any]):
        if key not in self.data_cache.keys():
            self.data_cache[key] = dict()
        if sub_key not in self.data_cache[key].keys():
            self.data_cache[key][sub_key] = dict()
        if sub_sub_key not in self.data_cache[key][sub_key].keys():
            self.data_cache[key][sub_key][sub_sub_key] = data
        else:
            self.data_cache[key][sub_key][sub_sub_key].update(data)

    def write_data(self):
        with open("%s/%s_%s.json" % (self.directory_path, self.name, self.day_key), 'w') as stats_file:
            json.dump(self.data_cache, stats_file, sort_keys=True, indent=4)
