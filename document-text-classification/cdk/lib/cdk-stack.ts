import { Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as path from 'path';


export class CdkStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    //Role
    const lambdaExecutionRole = new iam.Role(
      this, 
      'lambda-textract-execution-role',
      {
        assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com')
      }
    )
    lambdaExecutionRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSLambdaBasicExecutionRole"));
    lambdaExecutionRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonTextractFullAccess"));

    // Lambda
    // const lambdaFunctionName = this.node.tryGetContext('lambdafn') || 'textract-upload-document';
    // const lambdaFunction = lambda.Function.fromFunctionArn(
    //   this,
    //   lambdaFunctionName,
    //   `arn:aws:lambda:${Stack.of(this).region}:${Stack.of(this).account}:function:${lambdaFunctionName}`
    // )
    // console.log('functionName', importedLambda.functionName)

    const lambdaFunction = new lambda.Function(this, 'textract-process-document', {
      runtime: lambda.Runtime.PYTHON_3_8,
      memorySize: 128,
      timeout: Duration.seconds(5),
      handler: 'lambda_process_document.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/')),
      role: lambdaExecutionRole
    });


    // API Gateway
    const api = new apigateway.RestApi(
      this,
      'smart-doc-api-cdk', {
      binaryMediaTypes: ['*/*'],
      description: 'Smart Document Analysis API using AWS CDKv2',
      deployOptions: {
        stageName: 'v1',
        // loggingLevel: apigateway.MethodLoggingLevel.INFO
      }
    });
    const identify = api.root.addResource('identify');

    const getLambdaIntegration = new apigateway.LambdaIntegration(
      lambdaFunction,
      {
        contentHandling: apigateway.ContentHandling.CONVERT_TO_TEXT,
        proxy: false,
        passthroughBehavior: apigateway.PassthroughBehavior.WHEN_NO_TEMPLATES,
        requestTemplates: {
          "image/png": '{\"base64Image\": \"$input.body\"}',
          "image/jpeg": '{\"base64Image\": \"$input.body\"}',
          'application/pdf': '{\"base64Image\": \"$input.body\"}',
        },
        integrationResponses: [
          {
            statusCode: '200',
            responseTemplates: {
              'application/json': ''
            }
          }
        ]
      }
    )

    identify.addMethod('PUT', getLambdaIntegration, {
      methodResponses: [
        { statusCode: '200' }
      ],
    });
  }
}
