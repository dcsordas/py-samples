import logging
import re
from datetime import datetime


class Processor(object):
    FILE_TYPE = None

    # TODO rename these in some smarter way
    MATCH_EMAIL = re.compile(r'\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?')
    DATETIME_TEMPLATES = (
        '%d-%m-%y',
        '%d-%m-%Y',
        '%d/%m/%y',
        '%d/%m/%Y'
    )
    NULL_VALUES = None

    def __init__(self):
        self.log = logging.getLogger(f'pipeline.processors.{self.__class__.__name__}')

    @classmethod
    def get_instance(cls, file_type):
        if cls.FILE_TYPE == file_type:
            return cls()
        for sub in cls.__subclasses__():
            return sub.get_instance(file_type)

    def process(self, item):
        return self._process_item(item)

    def _process_item(self, item):
        raise NotImplementedError()

    def _process_text_field(self, value, nullable=True, strict=False):
        if not value or value.lower() in self.NULL_VALUES:
            if nullable and not strict:
                return None
            raise ValueError(f"'{value}' is null")
        return value

    def _process_email_field(self, value, nullable=True, strict=False):
        if not value or not self.MATCH_EMAIL.fullmatch(value):
            if nullable and not strict:
                return None
            raise ValueError(f"'{value}' is not a valid email address")
        return value

    def _process_date_field(self, value, nullable=True, strict=False):
        if value:
            date_value = None
            for dt_format in self.DATETIME_TEMPLATES:
                try:
                    date_value = datetime.strptime(value, dt_format).date()
                    break
                except ValueError:
                    continue
            if date_value or not strict:
                return date_value
            return date_value
        elif nullable and not strict:
            return None
        raise ValueError(f"'{value}' is not a valid date")


class CsvProcessor(Processor):
    FILE_TYPE = 'csv'

    DATETIME_TEMPLATES = (
        '%d-%m-%y',
        '%d-%m-%Y',
        '%d/%m/%y',
        '%d/%m/%Y'
    )
    NULL_VALUES = (
        'n/a',
        '/',
        '-'
    )

    def _process_item(self, item):
        processed = {}
        for key, value in item.items():
            try:
                key = key.strip()
                value = value.strip()
                if key == 'Name':
                    processed['name'] = self._process_text_field(value, nullable=False, strict=True)
                elif key == 'Email':
                    processed['email'] = self._process_email_field(value, nullable=False, strict=True)
                elif key == 'Comment':
                    processed['comment'] = self._process_text_field(value, nullable=True)
                elif key == 'Created At':
                    processed['created_at'] = self._process_date_field(value, nullable=True)
                else:
                    raise ValueError(f"'{key}' is an unknown entry")
            except Exception as error:
                self.log.exception(error)
        return processed
