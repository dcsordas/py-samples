import logging
from csv import DictReader
import os

__file_cache = set()


def _is_file_valid(path, filename):
    return os.path.isfile(os.path.join(path, filename)) and filename not in __file_cache


def scan_input_dir(input_dir, validator_function=_is_file_valid):
    return [
        os.path.join(input_dir, f)
        for f
        in os.listdir(input_dir)
        if validator_function(input_dir, f)
    ]


def with_file_cache(f):
    def wrapper(self, *args, **kwargs):
        r = f(self, *args, **kwargs)
        if r:
            __file_cache.add(self.filename)
        return r
    return wrapper


class Extractor(object):
    FILE_EXTENSION = None
    file_path = None
    log = None

    def __init__(self, file_path):
        self.file_path = file_path
        self.log = logging.getLogger(f'pipeline.extractors.{self.__class__.__name__}')

    @classmethod
    def get_instance(cls, file_path):
        _, extension = os.path.splitext(file_path)
        if extension == cls.FILE_EXTENSION:
            return cls(file_path)
        for sub in cls.__subclasses__():
            return sub.get_instance(file_path)

    @property
    def filename(self):
        return os.path.split(self.file_path)[1]

    @with_file_cache
    def extract(self):
        return self._extract()

    def _extract(self):
        raise NotImplementedError


class CsvExtractor(Extractor):
    FILE_EXTENSION = '.csv'

    def _extract(self):
        try:
            with open(self.file_path, 'r') as f:
                reader = DictReader(f)
                data = [dict(data=row, file_type=self.FILE_EXTENSION[1:], file=self.filename) for row in reader]
                self.log.debug(f'extracted path={self.file_path} items={len(data)}')
            return data
        except Exception as error:
            self.log.exception(error)
            return None
