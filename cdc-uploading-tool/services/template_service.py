import io
import json
import os
import re

import pandas as pd

import openpyxl

from config.configuration import configs

VALID_TEMPLATE_EXTENSIONS = ['.xlsx', '.xls', '.csv']


def create_template(column_headers, template_id):
    print(f'Creating Excel template for fields {json.dumps(column_headers)}')
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    update_template_specific_headers(column_headers, template_id)
    print(f'Updated columns for template {template_id} arw {column_headers}')
    for col_num, field in enumerate(column_headers, 1):
        col_letter = openpyxl.utils.get_column_letter(col_num)
        worksheet[col_letter + '1'] = field
    excel_file = io.BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)
    return excel_file


def get_filled_template_data(file):
    extension = get_file_extension(file)
    if not extension or extension.lower() not in VALID_TEMPLATE_EXTENSIONS:
        raise ValueError('Unsupported file extension')
    if extension == 'csv':
        df = pd.read_csv(file, keep_default_na=False)
    else:
        df = pd.read_excel(file, keep_default_na=False)
    result = []
    for index, row in df.iterrows():
        data = {}
        for column, value in row.items():
            update_nested_dict(data, column.split('.'), value)
        result.append(data)
    print(f'Data from file: {json.dumps(result)}')
    return result


def update_nested_dict(data, keys, value):
    if len(keys) == 1:
        data[keys[0]] = value
    else:
        key = keys[0]
        if key not in data:
            data[key] = {}
        update_nested_dict(data[key], keys[1:], value)


def is_valid_file_extension(file):
    extension = get_file_extension(file)
    return extension in VALID_TEMPLATE_EXTENSIONS


def get_file_extension(file):
    _, extension = os.path.splitext(file.filename)
    return extension.lower()


def update_template_specific_headers(headers, template_id):
    PREFIX_REGEX_KEY = 'prefixRegex'
    PREFIX_KEY = 'prefix'

    for template_config in configs['cdc.templates']:
        if template_config['key'] == template_id:
            replacement_fields = template_config.get('replacements', [])
            part_replacement_fields = template_config.get('partReplacements', [])
            static_fields = template_config.get('staticFields', [])

    # replacing replacement fields
    for field in replacement_fields:
        if field['key'] in headers:
            headers[headers.index(field['key'])] = field['value']

    # replacing part replacements fields
    for field in part_replacement_fields:
        for ind, header in enumerate(headers):
            if header.startswith(field['key']):
                headers[ind] = header.replace(field['key'], field['value'], 1)

    # replacing static fields
    for field in static_fields:
        if PREFIX_REGEX_KEY in field:
            print('Inside prefix check')
            for ind, header in enumerate(headers.copy()):
                if re.compile(field[PREFIX_REGEX_KEY]).match(header):
                    for static_field in field['fields']:
                        headers.append(header + '.' + static_field)
                    if not field['includePrefixField']:
                        headers.remove(header)
        elif PREFIX_KEY in field:
            pass
