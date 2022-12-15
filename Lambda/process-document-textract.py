import json
import urllib.parse
import boto3
import base64
from pprint import pprint
import re

print('Loading function')

textractClient = boto3.client('textract')
s3 = boto3.client('s3')

DOCUMENT_TYPE_ENUM = {
    'passport': 'PASSPORT',
    'identity_card': 'IDENTITY_CARD',
    'driving_license': 'DRIVER_LICENSE'
}

COUNTRY_ENUM = {
    'ID': 'INDONESIA',
    'PH': 'PHILIPPINES',
    'TH': 'THAILAND',
    'VN': 'VIETNAM',
    'MY': 'MALAYSIA',
}

DRIVER_LICENSE_RESP = {
    'country': '',
    'documentType': 'DRIVER_LICENSE',
    'extract_response':{
        'LASTNAME': 'TEST LAST',
        'FIRSTNAME': 'TEST FIRST',
        'MIDDLENAME': 'TEST MIDDLE',
        'DATE_OF_BIRTH': '11/27/1985',
        'ADDRESS': 'TEST LAST',
        'LICENSE_NUMBER': '124214-6456-675',
        'EXPIRATION_DATE': '11/27/2025',
        'AGENCY_CODE': '0TH',
        'RESTRICTIONS': 'TEST LAST',
        'CONDITIONS': '124214-6456-675',
        'BLOOD_TYPE': '11/27/2025',
        'EYES_COLOR': '0TH',
        'SEX': '0TH',
        'HEIGHT_METER': 'TEST LAST',
        'WEIGHT_KG': '124214-6456-675'
    }
}

DRIVER_LICENSE = {
    'LASTNAME': '',
    'FIRSTNAME': '',
    'MIDDLENAME': '',
    'DATE_OF_BIRTH': '',
    'ADDRESS': '',
    'LICENSE_NUMBER': '',
    'EXPIRATION_DATE': '',
    'AGENCY_CODE': '',
    'RESTRICTIONS': '',
    'CONDITIONS': '',
    'BLOOD_TYPE': '',
    'EYES_COLOR': '',
    'SEX': '0TH',
    'HEIGHT_METER': '',
    'WEIGHT_KG': ''
}

IDENTITY_CARD_RESP = {
    'country': '',
    'documentType': 'IDENTITY_CARD',
    'extract_response':{
        'LASTNAME': '',
        'FIRSTNAME': '',
        'MIDDLENAME': '',
        'DATE_OF_BIRTH': '11/27/1985',
        'PLACE_OF_BIRTH': '11/27/1985',
        'ADDRESS': 'TEST LAST' ,
        'IDENTITY_NUMBER': '124214-6456-675',
        'EXPIRATION DATE': '11/27/2025',
        'SEX': '0TH',
        'NATIONALITY': '',
        'OCCUPATION': ''
    }
}

IDENTITY_CARD = {
    'LASTNAME': '',
    'FIRSTNAME': '',
    'MIDDLENAME': '',
    'DATE_OF_BIRTH': '',
    'PLACE_OF_BIRTH': '',
    'ADDRESS': '',
    'IDENTITY_NUMBER': '',
    'EXPIRATION DATE': '',
    'SEX': '',
    'NATIONALITY': '',
    'OCCUPATION': ''
}

PASSPORT_RESP = {
    'country': '',
    'documentType': 'PASSPORT',
    'extract_response':{
        'PASSPORT_NUMBER': '',
        'FULLNAME': '',
        'NATIONALITY': '',
        'DATE_OF_BIRTH': '11/27/1985',
        'PLACE_OF_BIRTH': '11/27/1985',
        'SEX': '0TH',
        'HEIGHT': '0TH',
        'DATE_OF_ISSUE': '2021-10-10',
        'DATE_OF_EXPIRY': '2025-10-10'
    }
}

PASSPORT = {
    'FULLNAME': '',
    'NATIONALITY': '',
    'DATE_OF_BIRTH': '',
    'PLACE_OF_BIRTH': '',
    'SEX': '',
    'HEIGHT': '',
    'DATE_OF_ISSUE': '',
    'DATE_OF_EXPIRY': ''
}

def textract_analyze_form_s3(client, bucket, document):
    resp = {}
    try:
        resp = client.analyze_document(
            Document={'S3Object': {'Bucket': bucket, 'Name': document}},
            FeatureTypes=['FORMS']
            )
    except Exception as e:
        print('Error processing form analysis:', e)
        resp = {}
    return resp

def textract_detect_text_s3(client, bucket, document):
    resp = {}
    try:
        resp = client.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': document}}
            )
    except Exception as e:
        print('Error processing text detection:', e)
        resp = {}
    return resp

def textract_analyze_form_docs(client, image):
    resp = {}
    try:
        resp = client.analyze_document(
            Document={'Bytes': base64.b64decode(image)},
            FeatureTypes=['FORMS']
            )
    except Exception as e:
        print('Error processing form analysis:', e)
        resp = {}
    return resp

def textract_detect_text_docs(client, image):
    resp = {}
    try:
        resp = client.detect_document_text(
            Document={'Bytes': base64.b64decode(image)}
            )
    except Exception as e:
        print('Error processing text detection:', e)
        resp = {}
    return resp

def textract_process_s3(client, bucket, document):
    resp = {}
    try:
        resp = textract_detect_text_s3(client, bucket, document)
        # resp = textract_analyze_form_s3(client, bucket, document)
    except Exception as e:
        print('Error processing textract-s3')
        print('Error:', e)
        resp = {}
    return resp

def textract_process_docs(client, image):
    resp = {}
    try:
        # resp = textract_detect_text_docs(client, image)
        resp = textract_analyze_form_docs(client, image)
    except Exception as e:
        print('Error processing textract-s3')
        print('Error:', e)
        resp = {}
    return resp

def get_lines_from_textract(textract_resp):
    blocks = textract_resp['Blocks']
    linelist = []
    for item in blocks:
        if item['BlockType'] == 'LINE':
            # print(item['Text'])
            linelist.append(item['Text'])
    # print(linelist)
    return linelist

def get_words_from_textract(textract_resp):
    blocks = textract_resp['Blocks']
    wordlist = []
    for item in blocks:
        if item['BlockType'] == 'WORD':
            # print(item['Text'])
            wordlist.append(item['Text'])
    # print(wordlist)
    return wordlist

def parse_key_value(textract_response):

    key_map, value_map, block_map, lineblock_list = get_kv_map(textract_response)
    # pprint(value_map)

    # Get Key Value relationship
    kvs = get_kv_relationship(key_map, value_map, block_map)
    # print("\n\n== FOUND KEY : VALUE pairs ===\n")
    # print_kvs(kvs)

    return kvs

def get_kv_map(response):

    # Get the text blocks
    blocks=response['Blocks']

    # get key and value maps
    key_map = {}
    value_map = {}
    block_map = {}
    lineblock_list = []
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block
        if block['BlockType'] == "LINE":
            lineblock_list.append(block)

    return key_map, value_map, block_map, lineblock_list

def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    val_dict = {}
    position = []
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        top = round(key_block['Geometry']['BoundingBox']['Top'], 2)
        position.append(top)
        left = round(key_block['Geometry']['BoundingBox']['Left'], 2)
        confidence = key_block['Confidence']
        val = get_text(value_block, block_map)
        val_dict = {
            # 'key': key,
            'values': val,
            'confidence': confidence,
            'top': top,
            'left': left,
        }

        kvs[key] = val_dict
    ordered_kvs = {}
    # ordered_key = sorted(kvs, key=lambda k: kvs[k]['top'])
    ordered_key = sorted(kvs, key=lambda k: (kvs[k]['top'], kvs[k]['left']))
    ordered_kvs = {k: kvs[k] for k in ordered_key}
    
    return ordered_kvs

def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block

def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '    

                                
    return text

def get_position(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '    

                                
    return text

def parse_lines(textract_response):
    key_map, value_map, block_map, lineblock_list = get_kv_map(textract_response)
    linelist = get_lines(lineblock_list)
    std_lines = build_per_lines_text(linelist)
    return std_lines

def get_lines(linesblock_list):
    linetext_list  = []
    line_map = {}
    line_map_list = []
    for item in linesblock_list:
        linetext_list.append(item['Text'])
        line_id = item['Id']
        line_text = item['Text']
        line_confidence = item['Confidence']
        line_top = round(item['Geometry']['BoundingBox']['Top'], 2)
        line_left = round(item['Geometry']['BoundingBox']['Left'], 2)
        line_map = {
            'line_id': line_id,
            'line_text': line_text,
            'line_top': line_top,
            'line_left': line_left,
            'line_confidence': line_confidence,
        }
        line_map_list.append(line_map)
    
    # Sort lines based on top value:
    sortedlines = sorted(line_map_list, key=lambda d: (d['line_top'], d['line_left']))
    # pprint(sortedlines)
    return sortedlines

def build_per_lines_text(linelist):
    text = ''
    line_text = []
    current_top = 0
    for item in linelist:
        top = item['line_top']
        if top == current_top:
            text += item['line_text'] + ' '
        else:
            line_text.append(text)
            text = item['line_text']
        current_top = top
    # fill with empty string:
    line_text = line_text + [''] * (30 - len(line_text))
    return line_text[1:]

def parse_passport_id(textract_list, country):
    passport_id = 'PASSPORT-1234'
    passport_id_regex = re.compile('^\w{1,2}\s?\d{1,}$')
    passport_my_regex = re.compile('^A\s?\d{8}$')
    passport_th_regex = re.compile('^\w{1,2}\d{6,7}\w{0,1}$')
    passport_vn_regex = re.compile('^\w{1,2}\d{6,7}\w{0,1}$')
    passport_ph_regex = re.compile('^\w{1,2}\d{6,7}\w{0,1}$')

    if country == 'ID':
        passport_id_list = list(filter(passport_id_regex.match, textract_list))
    if country == 'MY':
        passport_id_list = list(filter(passport_my_regex.match, textract_list))
    if country == 'PH':
        passport_id_list = list(filter(passport_ph_regex.match, textract_list))
    if country == 'TH':
        passport_id_list = list(filter(passport_th_regex.match, textract_list))
    if country == 'VN':
        passport_id_list = list(filter(passport_vn_regex.match, textract_list))

    passport_id = passport_id_list[0] if passport_id_list else '',
    return passport_id

def parse_identity_id(textract_list, country):
    identity_id = 'IDENTITY-1234'
    identity_id_regex = re.compile('^\:?\s{0,2}\d{16}$')
    identity_my_regex = re.compile('^\d{6}\-\d{2}\-\d{4}$')
    identity_th_regex = re.compile('^\d{1}\s\d{4}\s\d{5}\s\d{2}\s\d{1}$')
    identity_vn_regex = re.compile('^[Ss]?[Oo]?\/?[Nn]?[Oo]?\:?\s{0,2}\d{9}$')
    identity_ph_regex = re.compile('')

    if country == 'ID':
        identity_id_list = list(filter(identity_id_regex.match, textract_list))
    if country == 'MY':
        identity_id_list = list(filter(identity_my_regex.match, textract_list))
    if country == 'PH':
        identity_id_list = list(filter(identity_ph_regex.match, textract_list))
    if country == 'TH':
        identity_id_list = list(filter(identity_th_regex.match, textract_list))
    if country == 'VN':
        identity_id_list = list(filter(identity_vn_regex.match, textract_list))

    identity_id = identity_id_list[0] if identity_id_list else '',
    return identity_id

def parse_driver_id(textract_list, country):
    driver_id = 'DRIVER-1234'
    driver_id_regex = re.compile('^\:?\s{0,3}(\d{4}-\d{4}-\d{6})|(\d{12})$')
    driver_my_regex = re.compile('^\:?\s{0,3}\d{12}$')
    driver_th_regex = re.compile('^\w{1,2}\d{6,7}\w{0,1}$')
    driver_vn_regex = re.compile('^\:?\s{0,3}\d{12}$')
    driver_ph_regex = re.compile('^\:?\s{0,3}\w\d{2}\-\d{2}-\d{6}$')

    if country == 'ID':
        driver_id_list = list(filter(driver_id_regex.match, textract_list))
    if country == 'MY':
        driver_id_list = list(filter(driver_my_regex.match, textract_list))
    if country == 'PH':
        driver_id_list = list(filter(driver_ph_regex.match, textract_list))
    if country == 'TH':
        driver_id_list = list(filter(driver_th_regex.match, textract_list))
    if country == 'VN':
        driver_id_list = list(filter(driver_vn_regex.match, textract_list))

    driver_id = driver_id_list[0] if driver_id_list else '',
    return driver_id

def identity_parser(kvs, country):
    IDENTITY_CARD = {
        'LASTNAME': '',
        'FIRSTNAME': '',
        'MIDDLENAME': '',
        'DATE_OF_BIRTH': '',
        'PLACE_OF_BIRTH': '',
        'ADDRESS': '',
        'IDENTITY_NUMBER': '',
        'EXPIRATION_DATE': '',
        'SEX': '',
        'NATIONALITY': '',
        'OCCUPATION': ''
    }
    # Indonesia
    if country == 'ID':
        IDENTITY_CARD['FIRSTNAME'] = kvs[3] if len(kvs) > 3 else ''
        IDENTITY_CARD['MIDDLENAME'] = kvs[3] if len(kvs) > 3 else ''
        IDENTITY_CARD['LASTNAME'] = ''
        IDENTITY_CARD['DATE_OF_BIRTH'] = kvs[4] if len(kvs) > 4 else ''
        IDENTITY_CARD['PLACE_OF_BIRTH'] = kvs[4] if len(kvs) > 4 else ''
        IDENTITY_CARD['ADDRESS'] = ' '.join(kvs[6:9]) if len(kvs) > 9 else ''
        IDENTITY_CARD['IDENTITY_NUMBER'] = kvs[3] if len(kvs) > 3 else ''
        IDENTITY_CARD['EXPIRATION_DATE'] = kvs[14] if len(kvs) > 14 else ''
        IDENTITY_CARD['SEX'] = kvs[5] if len(kvs) > 5 else ''
        IDENTITY_CARD['NATIONALITY'] = kvs[15] if len(kvs) > 15 else ''
        IDENTITY_CARD['OCCUPATION'] = kvs[13] if len(kvs) > 13 else ''

    # Malaysia
    if country == 'MY':
        IDENTITY_CARD['FIRSTNAME'] = kvs[4] if len(kvs) > 4 else ''
        IDENTITY_CARD['MIDDLENAME'] = kvs[4] if len(kvs) > 4 else ''
        IDENTITY_CARD['LASTNAME'] = kvs[4] if len(kvs) > 4 else ''
        IDENTITY_CARD['DATE_OF_BIRTH'] = ''
        IDENTITY_CARD['PLACE_OF_BIRTH'] = ''
        IDENTITY_CARD['ADDRESS'] = ' '.join([kvs[i] for i in [5,6,8]]) if len(kvs) > 9 else ''
        IDENTITY_CARD['IDENTITY_NUMBER'] = kvs[3] if len(kvs) > 3 else ''
        IDENTITY_CARD['EXPIRATION_DATE'] = kvs[14] if len(kvs) > 14 else ''
        IDENTITY_CARD['SEX'] = kvs[9] if len(kvs) > 9 else ''
        IDENTITY_CARD['NATIONALITY'] = kvs[7] if len(kvs) > 7 else ''
        IDENTITY_CARD['OCCUPATION'] = kvs[13] if len(kvs) > 13 else ''


    # Philippines
    if country == 'PH':
        IDENTITY_CARD['FIRSTNAME'] = kvs[8] if len(kvs) > 8 else ''
        IDENTITY_CARD['MIDDLENAME'] = kvs[11] if len(kvs) > 11 else ''
        IDENTITY_CARD['LASTNAME'] = kvs[6] if len(kvs) > 6 else ''
        IDENTITY_CARD['DATE_OF_BIRTH'] = kvs[15] if len(kvs) > 15 else ''
        IDENTITY_CARD['PLACE_OF_BIRTH'] = kvs[17] if len(kvs) > 17 else ''
        IDENTITY_CARD['ADDRESS'] = ' '.join([kvs[i] for i in [20, 22]]) if len(kvs) > 22 else ''
        IDENTITY_CARD['IDENTITY_NUMBER'] = kvs[4] if len(kvs) > 4 else ''
        IDENTITY_CARD['EXPIRATION_DATE'] = ''
        IDENTITY_CARD['SEX'] = kvs[13] if len(kvs) > 13 else ''
        IDENTITY_CARD['NATIONALITY'] = ''
        IDENTITY_CARD['OCCUPATION'] = ''
        pass

    # Thailand
    if country == 'TH':
        IDENTITY_CARD['FIRSTNAME'] = kvs[5] if len(kvs) > 5 else ''
        IDENTITY_CARD['MIDDLENAME'] = ''
        IDENTITY_CARD['LASTNAME'] = kvs[6] if len(kvs) > 6 else ''
        IDENTITY_CARD['DATE_OF_BIRTH'] = kvs[8] if len(kvs) > 8 else ''
        IDENTITY_CARD['PLACE_OF_BIRTH'] = ''
        IDENTITY_CARD['ADDRESS'] = ''
        IDENTITY_CARD['IDENTITY_NUMBER'] = kvs[1] if len(kvs) > 1 else ''
        IDENTITY_CARD['EXPIRATION_DATE'] = kvs[19] if len(kvs) > 19 else ''
        IDENTITY_CARD['SEX'] = ''
        IDENTITY_CARD['NATIONALITY'] = ''
        IDENTITY_CARD['OCCUPATION'] = ''

    # Vietnam
    if country == 'VN':
        IDENTITY_CARD['FIRSTNAME'] = kvs[9] if len(kvs) > 9 else ''
        IDENTITY_CARD['MIDDLENAME'] = ''
        IDENTITY_CARD['LASTNAME'] = kvs[9] if len(kvs) > 9 else ''
        IDENTITY_CARD['DATE_OF_BIRTH'] = kvs[11] if len(kvs) > 11 else ''
        IDENTITY_CARD['PLACE_OF_BIRTH'] = kvs[14] if len(kvs) > 14 else ''
        IDENTITY_CARD['ADDRESS'] = kvs[16] if len(kvs) > 16 else ''
        IDENTITY_CARD['IDENTITY_NUMBER'] = kvs[7] if len(kvs) > 7 else ''
        IDENTITY_CARD['EXPIRATION_DATE'] = kvs[17] if len(kvs) > 17 else ''
        IDENTITY_CARD['SEX'] = kvs[12] if len(kvs) > 12 else ''
        IDENTITY_CARD['NATIONALITY'] = kvs[12] if len(kvs) > 12 else ''
        IDENTITY_CARD['OCCUPATION'] = ''
    
    return IDENTITY_CARD

def driver_parser(kvs, country):
    DRIVER_LICENSE = {
        'LASTNAME': '',
        'FIRSTNAME': '',
        'MIDDLENAME': '',
        'DATE_OF_BIRTH': '',
        'ADDRESS': '',
        'LICENSE_NUMBER': '',
        'EXPIRATION_DATE': '',
        'AGENCY_CODE': '',
        'RESTRICTIONS': '',
        'CONDITIONS': '',
        'BLOOD_TYPE': '',
        'EYES_COLOR': '',
        'SEX': '0TH',
        'HEIGHT_METER': '',
        'WEIGHT_KG': ''
    }

    # Indonesia
    if country == 'ID':
        DRIVER_LICENSE['LASTNAME'] = ' '.join([kvs[i] for i in [5]])
        DRIVER_LICENSE['FIRSTNAME'] = ' '.join([kvs[i] for i in [5]])
        DRIVER_LICENSE['MIDDLENAME'] = ''
        DRIVER_LICENSE['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [8]])
        DRIVER_LICENSE['ADDRESS'] = ''
        DRIVER_LICENSE['LICENSE_NUMBER'] = ' '.join([kvs[i] for i in [11, 12]])
        DRIVER_LICENSE['EXPIRATION_DATE'] = ' '.join([kvs[i] for i in [13]])
        DRIVER_LICENSE['AGENCY_CODE'] = ''
        DRIVER_LICENSE['RESTRICTIONS'] = ''
        DRIVER_LICENSE['CONDITIONS'] = ''
        DRIVER_LICENSE['BLOOD_TYPE'] = ''
        DRIVER_LICENSE['EYES_COLOR'] = ''
        DRIVER_LICENSE['SEX'] = ' '.join([kvs[i] for i in [6]])
        DRIVER_LICENSE['HEIGHT_METER'] = ' '.join([kvs[i] for i in [9]])
        DRIVER_LICENSE['WEIGHT_KG'] = ''

    # Malaysia
    if country == 'MY':
        DRIVER_LICENSE['LASTNAME'] = ' '.join([kvs[i] for i in [3]])
        DRIVER_LICENSE['FIRSTNAME'] = ' '.join([kvs[i] for i in [3]])
        DRIVER_LICENSE['MIDDLENAME'] = ''
        DRIVER_LICENSE['DATE_OF_BIRTH'] = ''
        DRIVER_LICENSE['ADDRESS'] = ' '.join([kvs[i] for i in [12,13,14,15]])
        DRIVER_LICENSE['LICENSE_NUMBER'] = ' '.join([kvs[i] for i in [5,6]])
        DRIVER_LICENSE['EXPIRATION_DATE'] = ' '.join([kvs[i] for i in [9,10]])
        DRIVER_LICENSE['AGENCY_CODE'] = ''
        DRIVER_LICENSE['RESTRICTIONS'] = ''
        DRIVER_LICENSE['CONDITIONS'] = ''
        DRIVER_LICENSE['BLOOD_TYPE'] = ''
        DRIVER_LICENSE['EYES_COLOR'] = ''
        DRIVER_LICENSE['SEX'] = ''
        DRIVER_LICENSE['HEIGHT_METER'] = ''
        DRIVER_LICENSE['WEIGHT_KG'] = ''

    # Philippines
    if country == 'PH':
        DRIVER_LICENSE['LASTNAME'] = ' '.join([kvs[i] for i in [7,8]])
        DRIVER_LICENSE['FIRSTNAME'] = ' '.join([kvs[i] for i in [7,8]])
        DRIVER_LICENSE['MIDDLENAME'] = ' '.join([kvs[i] for i in [7,8]])
        DRIVER_LICENSE['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [11]])
        DRIVER_LICENSE['ADDRESS'] = ''
        DRIVER_LICENSE['LICENSE_NUMBER'] = ' '.join([kvs[i] for i in [16]])
        DRIVER_LICENSE['EXPIRATION_DATE'] = ' '.join([kvs[i] for i in [16]])
        DRIVER_LICENSE['AGENCY_CODE'] = ' '.join([kvs[i] for i in [16]])
        DRIVER_LICENSE['RESTRICTIONS'] = ' '.join([kvs[i] for i in [18]])
        DRIVER_LICENSE['CONDITIONS'] = ' '.join([kvs[i] for i in [18]])
        DRIVER_LICENSE['BLOOD_TYPE'] = ' '.join([kvs[i] for i in [16]])
        DRIVER_LICENSE['EYES_COLOR'] = ''
        DRIVER_LICENSE['SEX'] = ' '.join([kvs[i] for i in [10]])
        DRIVER_LICENSE['HEIGHT_METER'] = ' '.join([kvs[i] for i in [10]])
        DRIVER_LICENSE['WEIGHT_KG'] = ' '.join([kvs[i] for i in [10]])

    # Thailand
    if country == 'TH':
        DRIVER_LICENSE['LASTNAME'] = ' '.join([kvs[i] for i in [8]])
        DRIVER_LICENSE['FIRSTNAME'] = ' '.join([kvs[i] for i in [8]])
        DRIVER_LICENSE['MIDDLENAME'] = ''
        DRIVER_LICENSE['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [11]])
        DRIVER_LICENSE['ADDRESS'] = ''
        DRIVER_LICENSE['LICENSE_NUMBER'] = ' '.join([kvs[i] for i in [12]])
        DRIVER_LICENSE['EXPIRATION_DATE'] = ' '.join([kvs[i] for i in [5]])
        DRIVER_LICENSE['AGENCY_CODE'] = ''
        DRIVER_LICENSE['RESTRICTIONS'] = ''
        DRIVER_LICENSE['CONDITIONS'] = ''
        DRIVER_LICENSE['BLOOD_TYPE'] = ''
        DRIVER_LICENSE['EYES_COLOR'] = ''
        DRIVER_LICENSE['SEX'] = ''
        DRIVER_LICENSE['HEIGHT_METER'] = ''
        DRIVER_LICENSE['WEIGHT_KG'] = ''

    # Vietnam
    if country == 'VN':
        DRIVER_LICENSE['LASTNAME'] = ''
        DRIVER_LICENSE['FIRSTNAME'] = ' '.join([kvs[i] for i in [6,7]])
        DRIVER_LICENSE['MIDDLENAME'] = ''
        DRIVER_LICENSE['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [8]])
        DRIVER_LICENSE['ADDRESS'] = ' '.join([kvs[i] for i in [11,12]])
        DRIVER_LICENSE['LICENSE_NUMBER'] = ' '.join([kvs[i] for i in [18]])
        DRIVER_LICENSE['EXPIRATION_DATE'] = ' '.join([kvs[i] for i in [20]])
        DRIVER_LICENSE['AGENCY_CODE'] = ' '.join([kvs[i] for i in [5]])
        DRIVER_LICENSE['RESTRICTIONS'] = ''
        DRIVER_LICENSE['CONDITIONS'] = ''
        DRIVER_LICENSE['BLOOD_TYPE'] = ''
        DRIVER_LICENSE['EYES_COLOR'] = ''
        DRIVER_LICENSE['SEX'] = ''
        DRIVER_LICENSE['HEIGHT_METER'] = ''
        DRIVER_LICENSE['WEIGHT_KG'] = ''

    return DRIVER_LICENSE

def passport_parser(kvs, country):
    PASSPORT = {
        'FULLNAME': '',
        'NATIONALITY': '',
        'DATE_OF_BIRTH': '',
        'PLACE_OF_BIRTH': '',
        'SEX': '',
        'HEIGHT': '',
        'DATE_OF_ISSUE': '',
        'DATE_OF_EXPIRY': '',
        'PASSPORT_NUMBER': ''
    }

    # Indonesia
    if country == 'ID':
        PASSPORT['FULLNAME'] = ' '.join([kvs[i] for i in [9]])
        PASSPORT['NATIONALITY'] = ' '.join([kvs[i] for i in [10]])
        PASSPORT['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [12]])
        PASSPORT['PLACE_OF_BIRTH'] = ' '.join([kvs[i] for i in [13]])
        PASSPORT['SEX'] = ' '.join([kvs[i] for i in [9]])
        PASSPORT['HEIGHT'] = ''
        PASSPORT['DATE_OF_ISSUE'] = ' '.join([kvs[i] for i in [16]])
        PASSPORT['DATE_OF_EXPIRY'] = ' '.join([kvs[i] for i in [16]])
        PASSPORT['PASSPORT_NUMBER'] = ' '.join([kvs[i] for i in [6]])

    # Malaysia
    if country == 'MY':
        PASSPORT['FULLNAME'] = ' '.join([kvs[i] for i in [6]])
        PASSPORT['NATIONALITY'] = ' '.join([kvs[i] for i in [7,9]])
        PASSPORT['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [12]])
        PASSPORT['PLACE_OF_BIRTH'] = ' '.join([kvs[i] for i in [13]])
        PASSPORT['SEX'] = ' '.join([kvs[i] for i in [15]])
        PASSPORT['HEIGHT'] = ' '.join([kvs[i] for i in [15]])
        PASSPORT['DATE_OF_ISSUE'] = ' '.join([kvs[i] for i in [17]])
        PASSPORT['DATE_OF_EXPIRY'] = ' '.join([kvs[i] for i in [19]])
        PASSPORT['PASSPORT_NUMBER'] = ' '.join([kvs[i] for i in [4]])

    # Philippines
    if country == 'PH':
        PASSPORT['FULLNAME'] = ' '.join([kvs[i] for i in [7, 9, 5]])
        PASSPORT['NATIONALITY'] = ' '.join([kvs[i] for i in [11]])
        PASSPORT['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [11]])
        PASSPORT['PLACE_OF_BIRTH'] = ' '.join([kvs[i] for i in [13]])
        PASSPORT['SEX'] = ''
        PASSPORT['HEIGHT'] = ''
        PASSPORT['DATE_OF_ISSUE'] = ' '.join([kvs[i] for i in [15]])
        PASSPORT['DATE_OF_EXPIRY'] = ' '.join([kvs[i] for i in [17]])
        PASSPORT['PASSPORT_NUMBER'] = ' '.join([kvs[i] for i in [3]])

    # Thailand
    if country == 'TH':
        PASSPORT['FULLNAME'] = ' '.join([kvs[i] for i in [7]])
        PASSPORT['NATIONALITY'] = ' '.join([kvs[i] for i in [11]])
        PASSPORT['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [12]])
        PASSPORT['PLACE_OF_BIRTH'] = ' '.join([kvs[i] for i in [13]])
        PASSPORT['SEX'] = ' '.join([kvs[i] for i in [15]])
        PASSPORT['HEIGHT'] = ' '.join([kvs[i] for i in [15]])
        PASSPORT['DATE_OF_ISSUE'] = ' '.join([kvs[i] for i in [17]])
        PASSPORT['DATE_OF_EXPIRY'] = ' '.join([kvs[i] for i in [20]])
        PASSPORT['PASSPORT_NUMBER'] = ' '.join([kvs[i] for i in [2]])

    # Vietnam
    if country == 'VN':
        PASSPORT['FULLNAME'] = ' '.join([kvs[i] for i in [6]])
        PASSPORT['NATIONALITY'] = ' '.join([kvs[i] for i in [7]])
        PASSPORT['DATE_OF_BIRTH'] = ' '.join([kvs[i] for i in [10]])
        PASSPORT['PLACE_OF_BIRTH'] = ' '.join([kvs[i] for i in [10]])
        PASSPORT['SEX'] = ' '.join([kvs[i] for i in [12]])
        PASSPORT['HEIGHT'] = ''
        PASSPORT['DATE_OF_ISSUE'] = ' '.join([kvs[i] for i in [14]])
        PASSPORT['DATE_OF_EXPIRY'] = ' '.join([kvs[i] for i in [14]])
        PASSPORT['PASSPORT_NUMBER'] = ' '.join([kvs[i] for i in [4]])

    return PASSPORT


def check_document_type(resp):
    document_content = {}
    if resp['document_type'] == 'PASSPORT':
        document_content = PASSPORT
    if resp['document_type'] == 'DRIVER_LICENSE':
        document_content = DRIVER_LICENSE
    if resp['document_type'] == 'IDENTITY_CARD':
        document_content = IDENTITY_CARD
    return document_content

def parse_document(textract_resp):
    resp = {
        'document_type': 'unidentified', # Identity Card | Driver License | Unidentified
        'country': 'unidentified', # Indonesia | Malaysian | Thailand | Phillipines | Vietnam
        'textract_response': {},
        'key_values': {}
    }

    if textract_resp == {}:
        return resp

    kv = parse_key_value(textract_resp)
    print('key values', kv)
    item_list = list(kv.items())
    resp['key_values'] = kv
    standardized_lines = parse_lines(textract_resp)

    linelist = get_lines_from_textract(textract_resp)
    linelist_standardized = [w.lower() for w in linelist]
    print('linelist:', linelist_standardized)
    wordlist = get_words_from_textract(textract_resp)
    wordlist_standardized = [w.lower() for w in wordlist]
    resp['context'] = linelist
    print(wordlist_standardized)
    
    # Passport
    PASSPORT_PHRASE = ['passport', 'paspor', 'pasaporte', 'pasport', 'hô chiéu']
    if any(x in wordlist_standardized for x in PASSPORT_PHRASE):
        if 'indonesia' in wordlist_standardized:
            resp['document_type'] = DOCUMENT_TYPE_ENUM['passport']
            resp['country'] = COUNTRY_ENUM['ID']
            resp['textract_response'] = passport_parser(standardized_lines, 'ID')
            print(resp)
            return resp

        if 'malaysia' in wordlist_standardized:
            resp['document_type'] = DOCUMENT_TYPE_ENUM['passport']
            resp['country'] = COUNTRY_ENUM['MY']
            resp['textract_response'] = passport_parser(standardized_lines, 'TH')
            return resp

        if 'philippines' in wordlist_standardized:
            resp['document_type'] = DOCUMENT_TYPE_ENUM['passport']
            resp['country'] = COUNTRY_ENUM['PH']
            resp['textract_response'] = passport_parser(standardized_lines, 'PH')
            return resp

        if 'thailand' in wordlist_standardized or 'thai' in wordlist_standardized:
            resp['document_type'] = DOCUMENT_TYPE_ENUM['passport']
            resp['country'] = COUNTRY_ENUM['TH']
            resp['textract_response'] = passport_parser(standardized_lines, 'TH')
            return resp

        if 'vietnam' in wordlist_standardized:
            resp['document_type'] = DOCUMENT_TYPE_ENUM['passport']
            resp['country'] = COUNTRY_ENUM['VN']
            resp['textract_response'] = passport_parser(standardized_lines, 'VN')
            return resp

    # Indonesian
    if 'nik' in linelist_standardized or 'provinsi' in linelist_standardized:
        resp['document_type'] = DOCUMENT_TYPE_ENUM['identity_card']
        resp['country'] = COUNTRY_ENUM['ID']
        resp['textract_response'] = identity_parser(standardized_lines, 'ID')
        return resp
    
    if 'surat izin mengemudi' in linelist_standardized or 'kepolisian negara' in linelist_standardized:
        print(DOCUMENT_TYPE_ENUM)
        resp['document_type'] = DOCUMENT_TYPE_ENUM['driving_license']
        resp['country'] = COUNTRY_ENUM['ID']
        resp['textract_response'] = driver_parser(standardized_lines, 'ID')
        return resp

    # Phillipines
    if 'philippine identification card' in linelist_standardized:
        resp['document_type'] = DOCUMENT_TYPE_ENUM['identity_card']
        resp['country'] = COUNTRY_ENUM['PH']
        resp['textract_response'] = identity_parser(standardized_lines, 'PH')
        return resp

    if all(x in linelist_standardized for x in ['land transportation office', 'republic of the philippines']):
        resp['document_type'] = DOCUMENT_TYPE_ENUM['driving_license']
        resp['country'] = COUNTRY_ENUM['PH']
        resp['textract_response'] = driver_parser(standardized_lines, 'PH')
        return resp

    # Malaysian
    if 'MyKad' in linelist_standardized or 'kad pengenalan malaysia' in linelist_standardized or 'malaysia' in linelist_standardized:
        resp['document_type'] = DOCUMENT_TYPE_ENUM['identity_card']
        resp['country'] = COUNTRY_ENUM['MY']
        resp['textract_response'] = identity_parser(standardized_lines, 'MY')
        return resp

    if 'lesen memandu' in linelist_standardized or all(x in linelist_standardized for x in ['driving license', 'malaysia']):
        resp['document_type'] = DOCUMENT_TYPE_ENUM['driving_license']
        resp['country'] = COUNTRY_ENUM['MY']
        resp['textract_response'] = driver_parser(standardized_lines, 'MY')
        return resp

    # Thailand
    if 'thai' in linelist_standardized or 'thai national id card' in linelist_standardized:
        resp['document_type'] = DOCUMENT_TYPE_ENUM['identity_card']
        resp['country'] = COUNTRY_ENUM['TH']
        resp['textract_response'] = identity_parser(standardized_lines, 'TH')
        return resp

    if all(x in linelist_standardized for x in ['driving license', 'kingdom of thailand']):
        resp['document_type'] = DOCUMENT_TYPE_ENUM['driving_license']
        resp['country'] = COUNTRY_ENUM['TH']
        resp['textract_response'] = driver_parser(standardized_lines, 'TH')
        return resp

    # Vietnam
    if 'socialist republic of vietnam' in linelist_standardized or 'socialist republic of viet nam' in linelist_standardized or 'citizen identity card' in linelist_standardized:
        resp['document_type'] = DOCUMENT_TYPE_ENUM['identity_card']
        resp['country'] = COUNTRY_ENUM['VN']
        resp['textract_response'] = identity_parser(standardized_lines, 'VN')
        return resp

    if all(x in wordlist_standardized for x in ['license', 'viêt', 'nam']):
        resp['document_type'] = DOCUMENT_TYPE_ENUM['driving_license']
        resp['country'] = COUNTRY_ENUM['VN']
        resp['textract_response'] = driver_parser(standardized_lines, 'VN')
        return resp
    
    return resp

def build_response(resp):
    document_content = check_document_type(resp)
    resp_v1 = {
        'statusCode': 200,
        'body': {
            'country': resp['country'],
            'document_type':resp['document_type'],
            'textract_response': document_content
        }
    }

    resp_v2 = {
        'country': resp['country'],
        'document_type':resp['document_type'],
        'textract_response': document_content
    }

    resp_v3 = {
        'country': resp['country'],
        'document_type':resp['document_type'],
        'textract_response': resp['textract_response'],
        'key_values': resp['key_values']
    }
    
    return resp_v3

def get_data(event):
    print('event:',event)
    filename = event['filename']
    bucket = 'swift4-documents-encoded'
    response = s3.get_object(Bucket=bucket,Key=filename)
    text= response["Body"].read().decode('utf-8') 
    print(text)
    data = json.loads(text)
    return data
    
def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    print(event)

    data=get_data(event) 
    #imageBase64 = event['base64Image']
    imageBase64 = data['base64Image']
    # print(type(imageBase64))
    resp = textract_process_docs(textractClient, imageBase64)
    # print('textract response:', resp)

    parsed_resp = parse_document(resp)
    print(parsed_resp)
    
    final_response = build_response(parsed_resp)

    filename = event['filename']  
    body_response ={
        "function_name": "process-document",
        "filename" :filename,
        "response" : final_response
    }
    return {
        'statusCode': 200,
        'body': body_response
    }
