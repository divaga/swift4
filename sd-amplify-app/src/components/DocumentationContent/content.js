export const content= {
    overview: 'This Smart Document Identification application is a machine learning powered application that is able to identify National ID, Driving License and Passport from 5 countries (Indonesia, Malaysia, Philippines, Thailand and Vietnam). This document identification leverages two methods of classification: image based identification and text based identification. This application is built using AWS Amplify with support from Amazon SageMaker and Amazon Textract works under the hood to classify uploaded images.',
    features:{
        text:'Following are features for this document identification application:',
        details:[
            " - Scalable web application with integrated user authentication",
            " - Ability to classify national ID, driving license and passport from 5 countries",
            " - Classify input images based on image classification, this image classification is trained for 3 documents from 5 countries",
            " - Classify input images based on extracted text from those document",
            " - Extract document entities based on specific document type"
            ]
    },
    imageclasssification:{
        text:'Image Classification API is using Amazon SageMaker Endpoint hosted SageMaker model pretrained with around 280 training images with 15 classes. This model trained using SageMaker Image Classification algorithm with additional image augmentation process (rotate, sharpen and contrast) applied in this training datasets. Since this application was designed to do real-time image classification, we are using SageMaker instead of Amazon Rekognition Custom Label for cost optimization.'
    },
    textclassification:{
        text:'Document Text Classification leverages Textract API which uses OCR to parse text from image and PDF documents. Textract API reads texts in the identity document and return scanned texts and form values. Document Text Classification endpoints then parses and uses programmatic logic based on unique identity document content to classify country and document type of the parsed document. Document Text Classification returns key-value based form values to list down all identity data within the document.'
    },
    architecture:{
        text:'architecture description <TBD>'
    },
    appflow:{
        text:'architecture description <TBD>',
        flows:[
            {seq:1,text:'User authenticate to application with Amplify Auth'},
            {seq:2,text:'User upload document via REST API /identify'},
            {seq:3,text:'API Gateway validate authenticated API request'},
            {seq:4,text:'API Gateway invoke REST API LambdaUpload handler'},
            {seq:6,text:'Upload Handler invokes Step Function to process document with filename of base64encoded JSON file'},
            {seq:7,text:'Step Function initiates workflow execution to process document'},
            {seq:8,text:'Step Function returns execution ARN ID to Upload Handler'},
            {seq:9,text:'Upload Handler returns execution ARN ID to client'},
            {seq:10,text:'API Gateway returns execution ARN ID to client'},
            {seq:11,text:'Client sends WebSocket message with execution ARN'},
            {seq:12,text:'API Gateway invokes Message Handler Lambda with execution ARN and session ID'},
            {seq:13,text:'Message Handler Lambda saves execution ARN and session ID in DynamoDB'},
            {seq:14,text:'Document Identification Workflow Lambda’s retrieve the base64encoded JSON in S3'},
            {seq:15,text:'Process Document Lambda extract the text from the document using Amazon Textract'},
            {seq:16,text:'Identify Document Lambda identifies the type of document using ML models with Sagemaker'},
            {seq:17,text:'Extract execution ARN from Step Function Workflow'},
            {seq:18,text:'Aggregate result from Process Document, Identify Document and extract execution ARN Lambdas'},
            {seq:19,text:'Send result of document processing and execution ARN to Response Handler Lambda'},
            {seq:20,text:'Query session ID from DynamoDB based on execution ARN'},
            {seq:21,text:'Response Handler Lambda sends session ID and document processing result to API Gateway Websocket API'},
            {seq:22,text:'API Gateway Websocket API returns the response to the client with the assigned session ID'}
        ]
        
    },
    usage:{
        text:'Upload supported document in this application in format of PNG or JPG within 5MB or less. This application will return these following output:',
        details:[
            " - Document classification based on image classification with confidence value",
            " - Document classification based on extracted text classification",
            " - Result of extracted text based on document class",
            ]
    },
    resources:{
        text:'All assets used by this application can be accessed here:',
        link:'https://github.com/divaga/swift4',
        details:[
            " - Document classification based on image classification with confidence value",
            " - Document classification based on extracted text classification",
            " - Result of extracted text based on document class",
            ]
    }
};