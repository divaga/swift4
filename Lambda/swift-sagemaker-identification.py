import json
import boto3
import base64

s3 = boto3.client('s3')

def getDocumentType(document):
    documentMap ={
        "ID_CITIZEN_ID" : "CITIZEN ID - INDONESIA",
        "ID_DRIVING_LICENSE" : "DRIVER LICENSE - INDONESIA",
        "ID_PASSPORT" : "PASSPORT - INDONESIA",
        "MY_CITIZEN_ID" : "CITIZEN ID - MALAYSIA",
        "MY_DRIVING_LICENSE" : "DRIVER LICENSE - MALAYSIA",
        "MY_PASSPORT" : "PASSPORT - MALAYSIA",
        "PH_CITIZEN_ID" : "CITIZEN ID - PHILIPPINES",
        "PH_DRIVING_LICENSE" : "DRIVER LICENSE - PHILIPPINES",
        "PH_PASSPORT" : "PASSPORT - PHILIPPINES",
        "TH_CITIZEN_ID" : "CITIZEN ID - THAILAND",
        "TH_DRIVING_LICENSE" : "DRIVER LICENSE - THAILAND",
        "TH_PASSPORT" : "PASSPORT - THAILAND",
        "VN_CITIZEN_ID" : "CITIZEN ID - VIETNAM",
        "VN_DRIVING_LICENSE" : "DRIVER LICENSE - VIETNAM",
        "VN_PASSPORT" : "PASSPORT - VIETNAM"
    }
    return documentMap[document];
    
def argmax(array):
  index, value = 0, array[0]
  for i,v in enumerate(array):
    if v > value:
      index, value = i,v
  return index

def get_data(event):
    filename = event['filename']
    bucket = 'swift4-documents-encoded'
    response = s3.get_object(Bucket=bucket,Key=filename)
    text= response["Body"].read().decode('utf-8') 
    print(text)
    data = json.loads(text)
    return data

def lambda_handler(event, context):
    
    #eventBody = json.loads(json.dumps(event))['body']
    #imageBase64 = json.loads(eventBody)['Image']
    data=get_data(event)

    #imageBase64 = event['base64Image']
    imageBase64 = data['base64Image']
    # sagemaker
    runtime_sm_client = boto3.client(service_name='sagemaker-runtime')

     # PLEASE CHANGE THIS BASED ON YOUR SAGEMAKER ENDPOINTS!
    ENDPOINT_NAME = 'swift-document-identification-endpoint'

    
    # get sagemaker prediction
    response = runtime_sm_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='image/jpeg',
            Body=base64.b64decode(imageBase64))
    
    prob = json.loads(response['Body'].read())
    # CHANGE THIS BASED ON YOUR CLASSES/FOLDER NAME IN ALFABHETICAL ORDER
    document_type = ['ID_CITIZEN_ID', 'ID_DRIVING_LICENSE', 'ID_PASSPORT','MY_CITIZEN_ID', 'MY_DRIVING_LICENSE', 'MY_PASSPORT','PH_CITIZEN_ID', 'PH_DRIVING_LICENSE', 'PH_PASSPORT','TH_CITIZEN_ID', 'TH_DRIVING_LICENSE', 'TH_PASSPORT','VN_CITIZEN_ID', 'VN_DRIVING_LICENSE', 'VN_PASSPORT']

    index = argmax(prob)
    #print("Result: label - " + document_type[index] + ", probability - " + str(prob[index]))
    result= {
        'document_image_classification':getDocumentType(document_type[index]),
        'imageclassification_confidence':str(prob[index])
    }
    filename = event['filename']
    body_response ={
        'function_name' : 'sagemaker-identification',
        'filename':filename,
        'response' : result
    }

    return {
        'statusCode': 200,
        'body': body_response
    }
