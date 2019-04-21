from csv import DictReader
from io import StringIO
from typing import List

from django.db.models.fields.files import FieldFile


class FieldFileCsvHelper:
    def read_csv_file(self, field_file: FieldFile):
        dict_reader = self._get_dict_reader(field_file)
        rows = list(dict_reader)
        header = self._get_csv_header(dict_reader)
        return rows, header

    def get_csv_header(self, field_file: FieldFile) -> List[str]:
        dict_reader = self._get_dict_reader(field_file)
        return self._get_csv_header(dict_reader)

    def _get_dict_reader(self, field_file: FieldFile):
        as_str = field_file.read().decode('utf-8')
        dict_reader = DictReader(StringIO(as_str), delimiter=',', quotechar='"')
        return dict_reader

    def _get_csv_header(self, dict_reader: DictReader):
        return dict_reader.fieldnames
