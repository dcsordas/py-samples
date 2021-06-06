import json
import logging
import os
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path


class Loader(object):
    DATE_FORMAT = '%a %d-%b-%Y'

    def __init__(self):
        self.log = logging.getLogger(f'pipeline.loaders.{self.__class__.__name__}')

    def dump(self, payload):

        # build path
        today = date.today()
        dir_path = Path(f'output/{today.year}/{today.month}/{today.day}')
        dir_path.mkdir(parents=True, exist_ok=True)

        # dump payload
        counter = defaultdict(lambda: 1)
        for item in payload:
            try:
                data = self._sanitise_item(item['data'])
                source_name = f'{os.path.splitext(item["file"])[0]}-{item["file_type"]}'
                filename = f'{source_name}-{counter[source_name]}.json'
                counter[source_name] += 1
                with open(os.path.join(dir_path, filename), 'w') as f:
                    json.dump(data, f)
            except Exception as error:
                self.log.exception(error)

    def _sanitise_item(self, item):
        processed = {}
        for key, value in item.items():
            if isinstance(value, (date, datetime)):
                value = value.strftime(self.DATE_FORMAT)
            processed[key] = value
        return processed
