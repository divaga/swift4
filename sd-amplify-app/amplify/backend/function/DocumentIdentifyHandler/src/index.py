import json
import urllib.parse
import boto3
import base64
import uuid

client = boto3.client('stepfunctions')
s3 = boto3.client('s3')

def buildStepFunctionData(event):
    body= event['body']
    print(type(body))
    print(body)
    json_body = json.loads(body)
    print(type(json_body))
    imageBase64Req = json_body['base64Image']
    print(type(imageBase64Req))
    print('imageBase64Req :' + str(imageBase64Req) )
    imageBase64Content=imageBase64Req.split(",")
    print('imageBase64Content :' + str(imageBase64Content) )
    print(type(imageBase64Content))
    imageBase64=imageBase64Content[1]
    print(imageBase64)
    data = {"base64Image":imageBase64}
    return data

def upload_data_s3(event,transactionId):
    data = buildStepFunctionData(event)
    bucket = 'swift4-documents-encoded'
    uploadByteStream = bytes(json.dumps(data).encode('UTF-8'))
    filename = transactionId +'.json'
    result = s3.put_object(Bucket=bucket,Key =filename, Body=uploadByteStream)
    print(result)
    
def handler(event, context):
    response = {}
    headers = {
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,PUT",
            "Access-Control-Allow-Origin": "*",
        }
    
    try:
        print("Received event: " + json.dumps(event))
        transactionId=str(uuid.uuid1())
        #data = buildStepFunctionData(event)
        #base64Image=data['base64Image']
        filename = transactionId +'.json'
        input = {"filename":filename}
        upload_data_s3(event,transactionId)
        execution_result = client.start_execution(
            stateMachineArn='arn:aws:states:ap-southeast-1:687821209850:stateMachine:SmartDocumentStateMachine',
            name=transactionId,
            input=json.dumps(input)
        )    
        print(' execution_result : ' + str(execution_result))
        executionArn = execution_result['executionArn']
    
        response = {"headers": headers,
            "statusCode": 200,
            "body": json.dumps({"statusCode": 200, "executionArn": executionArn })
            }

    except Exception as e:
        print('Error processing parsing uploaded file')
        print('Error:', e)
        response = {"headers": headers,
                    "statusCode": 500,
                    "body": json.dumps({"statusCode": 500, "error_msg":str(e) })
                    }
        
    return response
    