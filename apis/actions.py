from flask import jsonify, request, Response

from config.configuration import configs
from services import cdc_config_service as ccs
from services import cdc_integration_service as cis
from services import file_util as fl
from services import language_service as ls
from services import template_service as ts


def process_data():
    try:
        config_id = request.form.get('configId')
        if not ccs.get_cdc_config(config_id):
            raise ValueError('There is no available configuration with the configId {}'.format(config_id))
        else:
            if 'dataFile' not in request.files or request.files['dataFile'].filename == '':
                return create_response(False, message='No file provided', status_code=400), 400
            file = request.files['dataFile']
            if not ts.is_valid_file_extension(file):
                return create_response(False, message='Invalid file extension', status_code=400), 400
        result = ts.get_filled_template_data(file)
        if not result:
            raise ValueError('No data available in the uploaded file')
        return create_response(True, result, 'File upload successful!', 200), 200
    except ValueError as e:
        print('Error: ', str(e))
        return create_response(False, message='Invalid request: {}'.format(str(e)), status_code=403), 403
    except Exception as e:
        print('Internal error: ', str(e))
        return create_response(False, message='Internal error: {}'.format(str(e)), status_code=500), 500


def get_template():
    data = {}
    try:
        request_data = request.json
        config_id = request_data.get('configId')
        if not ccs.get_cdc_config(config_id):
            data = {'statusCode': 403}
            raise ValueError('Invalid configuration provided, please select configuration from saved values only')
        data = cis.get_account_schema_from_cdc(config_id)
        if data['statusCode'] >= 400:
            raise ValueError(f"Unable to fetch template details: {data['errorMessage']}")
        return create_response(True, data, 'Template data fetched successfully', 200), 200
    except ValueError as e:
        print(str(e))
        return create_response(False, message=str(e), status_code=data['statusCode']), data['statusCode']
    except Exception as e:
        print('Error in get_template: ', str(e))
        return create_response(False,
                               message=f'Error while getting template: {str(e)}. Please try again after sometime.',
                               status_code=500), 500


def create_template_file():
    data = request.json
    template_fields, template_id = data['selectedFields'], data['templateId']
    excel_file = ts.create_template(template_fields, template_id)
    return Response(
        excel_file,
        headers={
            'Content-Disposition': 'attachment',
            'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    )


def translate_text():
    try:
        data = request.json
        text = data['text']
        destination_language, source_language = data['destinationLanguage'], None
        if 'sourceLanguage' in data:
            source_language = data['sourceLanguage']
        if configs['translation.sap_ai.active']:
            translated_text = ls.ai_translate(text, source_language, destination_language, 'services.sap_ai_service')
        elif configs['translation.terryin.active']:
            translated_text = ls.terryin_translate(text, source_language, destination_language)
        elif configs['translation.openai.active']:
            translated_text = ls.ai_translate(text, source_language, destination_language, 'services.openai_service')
        else:
            raise RuntimeError('Translation service is not available currently, please try again after sometime')
        return create_response(True, {
            'translated_text': translated_text
        }, status_code=200), 200
    except (RuntimeError, Exception) as e:
        print('Error: ', str(e))
        return create_response(False, message=f'Error in translating content: {str(e)}', status_code=500), 500


def save_cdc_config():
    data = request.json
    try:
        ccs.update_cdc_config(data)
        success = True
        message = 'Config successfully updated'
        status_code = 200
    except Exception as e:
        success = False
        message = 'Unable to save config due to error: ' + str(e)
        status_code = 500
    return create_response(success, message=message, status_code=status_code), status_code


def send_data():
    data = request.json
    print(f'Request body for send_data request is {data}')
    try:
        result = cis.send_data_to_cdc(data['configId'], data['templateId'], data['data'])
        status_code = result['statusCode']
        if 200 <= status_code < 300: success = True
        else: success = False
        return create_response(success, result, status_code=status_code), status_code
    except Exception as e:
        print('Error in send_data: ', str(e))
        return create_response(False, {}, f'Unable to send data to CDC: {str(e)}', 500), 500


def get_all_cdc_configs():
    try:
        return create_response(True, list(ccs.load_cdc_configs().keys()), status_code=200), 200
    except Exception as e:
        print(f'Error while getting save configs: {str(e)}')
        return create_response(False, message=f'Error while fetching all configs: {str(e)}', status_code=500), 500


def export_cdc_response():
    data = request.json
    excel_file = fl.create_excel(data['headers'], data['data'])
    return Response(
        excel_file,
        headers={
            'Content-Disposition': 'attachment',
            'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    )

def create_response(success, result=None, message=None, status_code=None):
    response = {
        'success': success,
        'result': result,
        'statusCode': status_code
    }
    if message:
        response['message'] = message
    return jsonify(response)
