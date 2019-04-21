import csv
from csv import DictReader
from io import StringIO

from django.db.models.fields.files import FieldFile

from automatic_replenishment_system.retail_core.core.utils.file_utils import OSFileOperations


class FieldFileCsvHelper:
    def read_csv_file(self, field_file: FieldFile):
        dict_reader = self._get_dict_reader(field_file)
        rows = list(dict_reader)
        header = self._get_csv_header(dict_reader)
        return rows, header

    def _get_dict_reader(self, field_file: FieldFile):
        as_str = field_file.read().decode('utf-8')
        dict_reader = DictReader(StringIO(as_str), delimiter=',', quotechar='"')
        return dict_reader

    def _get_csv_header(self, dict_reader: DictReader):
        return dict_reader.fieldnames


class CSVInputOutput:
    def write_csv_to_file_dictwriter(self, file_name, header, rows, file_open_mode='w', extrasaction="raise"):
        file_exists = OSFileOperations.entity_exists(file_name)
        OSFileOperations.ensure_directory(file_name)
        with open(file_name, file_open_mode, encoding='utf8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL, extrasaction=extrasaction)
            if not file_exists or file_open_mode == 'w':
                writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def read_csv_file(self, csv_file):
        row_list = []
        csv.field_size_limit(100000000)
        with open(csv_file, 'r', newline='', encoding='utf-8') as bf:
            csvf = csv.DictReader(bf, delimiter=',', quotechar='"')
            field_names = csvf.fieldnames
            for row in csvf:
                row_list.append(row)
        return row_list, field_names
