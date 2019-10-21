import json
import pprint

DATA_DIR = 'data'


def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


class Source(object):
    storage = None

    def __init__(self, data_array=None):
        self.storage = {}
        for record in data_array or []:
            self.add(record)

    def __str__(self):
        return pprint.pformat(self.storage)

    def keys(self):
        return list(self.storage.keys())

    def get(self, key):
        return self.storage.get(key)

    def add(self, record):
        if self.storage.keys():
            key = max(self.storage.keys()) + 1
        else:
            key = 0
        self.storage[key] = record
        return key

    def update(self, key, record):
        if key in self.storage:
            self.storage[key] = record
            return key

    def delete(self, key):
        if key in self.storage:
            del self.storage[key]
            return key
