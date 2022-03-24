import React, { useEffect, useState} from "react";
import Button from "aws-northstar/components/Button";
import Stack from "aws-northstar/layouts/Stack";
import ColumnLayout, { Column } from 'aws-northstar/layouts/ColumnLayout';
import Container from 'aws-northstar/layouts/Container';
import { API , Auth } from 'aws-amplify';
import TextractResponse from '../../components/TextractResponse'
import FileUpload from 'aws-northstar/components/FileUpload';
import Flashbar from 'aws-northstar/components/Flashbar';
import Modal from 'aws-northstar/components/Modal';

import { w3cwebsocket as W3CWebSocket } from "websocket";

const client = new W3CWebSocket('wss://ctzj7kdire.execute-api.ap-southeast-1.amazonaws.com/dev');

const DocumentTaker = () => {
    
      useEffect(() => { 
          console.log("running useEffect");
          
          client.onerror  = (message) => {
            console.log('Connection Error');
            const response ={'statusCode':400,'message':message}
            buildWsStatusErroMessage(response);
          };
          
          client.onclose = (message) => {
            console.log('echo-protocol Client Closed');
          };
          
          client.onopen = () => {
            console.log('WebSocket Client Connected');
          };
          
         client.onmessage = (message) => {
            console.log(message);
            const data=message['data'];
            console.log(data);
            const response = JSON.parse(data);
            const responseType=response['responseType']
            const statusCode= response['statusCode']
            if(statusCode == 200 && responseType === 'IMAGE_UPLOAD'){
                buildWsSuccessMessage(response);
            }else{
                buildWsUnsupportedErroMessage(response);
            }
         };
      });
     
     const [uploadedFile, setUploadedFile] = useState(null);
     const [imgData, setImgData] = useState(null);
     const [error, setError] = useState(null);
     const [apiResponse, setApiResponse] = useState(null);
     const [wsResponse, setWsResponse] = useState(null);
     const [apiStatus, setApiStatus] = useState(null);
     const [visible, setVisible] = useState(false);
     const [selectedImage, setSelectedImage] = useState("Selected Image");
     
     const onFileUploadChanged = (files) => {
         console.log(files);
        if (files[0]) {
            setUploadedFile(files[0]);
            setSelectedImage(files[0].name);
            console.log("picture: ", files);
            const reader = new FileReader();
            reader.addEventListener("load", () => {
                setImgData(reader.result);
                setUploadedFile(reader.result);
            });
            reader.readAsDataURL(files[0]);
        }
    };
    
    const buildLoadingMessage = () =>{
        let message =[];
        const loading = {
            header: 'Document Submitted for Processing',
            content: 'The uploaded document have been submitted for document analysis',
            dismissible: true,
            loading: true
            }
            message.push(loading);
          
        setApiStatus(message);
    }
    
    const buildWsLoadingMessage = () =>{
        let message =[];
        const loading = {
            header: 'Document Submitted for Processing',
            content: 'The document submmitted is being analyzed.',
            dismissible: false,
            loading: true
            }
            message.push(loading);
         const data ={'wsStatus' : message }     
         setWsResponse(data);
    }
    
    const buildWsSuccessMessage = (response) =>{
        let message =[];
        const loading = {
            header: 'Document Analysis Completed',
            type:'success',
            content: 'Document analysis result received',
            dismissible: true
            }
            message.push(loading);
         const data ={'wsStatus' : message ,'body':response['body']} 
         
         setWsResponse(data);
    }
    
    const buildWsUnsupportedErroMessage = (response) =>{
        let message =[];
        console.log('buildWsUnsupportedErroMessage');
        const error = {
            header: 'Unsupported Document',
            type: 'error',
            content: response.body.message,
            dismissible: true
            }
        message.push(error);
        const data ={'wsStatus' : message } 
         
         setWsResponse(data);
    }   
    
    const buildWsStatusErroMessage = (response) =>{
        let message =[];
        console.log(response);
        const error = {
            header: 'Problem Connecting to WS Server',
            type: 'error',
            content: response.message,
            dismissible: true
            }
        message.push(error);
        const data ={'wsStatus' : message } 
         
         setWsResponse(data);
    }    
    
    const buildStatusMessage = (response) =>{
        
        let message =[];
        console.log(response);
        
        
        if(response.statusCode === 200){
            const success = {
            header: 'Document Submitted Successfully',
            type: 'success',
            content: 'The document have submitted for document analysis',
            dismissible: true
            }
            message.push(success);
        }else{
            const error = {
            header: 'Problem Encountered Processing Document',
            type: 'error',
            content: response.message,
            dismissible: true
            }
            message.push(error);
        }
        
        setApiStatus(message);
    }
    
    const sendExecutionArnToWS = (response) =>{
       console.log("response : " + response);
       const executionArn = response['executionArn'];
       console.log("executionArn : " + executionArn);
       const ws_message = {"action":"sendMessage" , "executionArn" : executionArn}
       client.send(JSON.stringify(ws_message));
    }
    
    const identifyDocument = async () => {
        setApiResponse(null);
        setWsResponse(null);
        if (uploadedFile === null) {
            setError("No file selected.");
            return;
        }

        buildLoadingMessage();
        
        
        console.log(`Using file ${uploadedFile}`);

        const apiName = 'SmartDocApi'; // replace this with your api name.
        const path = '/identify'; //replace this with the path you have configured on your API
        
        const formData = {base64Image: uploadedFile};
        console.log(formData);
        
        const myInit = {
            
            body: formData, // replace this with attributes you need
            headers: {
                Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}`,
            }, // OPTIONAL
        };

        API
            .put(apiName, path, myInit)
            .then(response => {
                 setApiResponse(response);
                 buildStatusMessage(response);
                 sendExecutionArnToWS(response);
                 buildWsLoadingMessage();
                 console.log('from apiResponse' + apiResponse);
                 console.log('from response' + response);
             })
            .catch(error => {
                 buildStatusMessage(error);
                 setError(error);
                 console.log(error);
            });
        
    };
    const imageStyle={
        display: "block",
        marginLeft: "auto",
        marginRight: "auto",
        width: "50%",
        height:"500px",
        objectFit:"contain",
        align:"center"
    }
    return (
        <div>
            { apiStatus !== null ? <Flashbar items={apiStatus} /> : <br/>}
            <Container headingVariant='h1' title="Document Identification">
                <ColumnLayout>
                    <Column key="column1">
                        <Stack spacing="xs">
                                 <Stack spacing="s">
                                     <FileUpload
                                      accept="image/jpeg,image/png"
                                      controlId="file1"
                                      label="Analyze your document"
                                      description="Document data will be processed using machine learning and will not be stored in the system"
                                      hintText="Document must be a file of type JPEG or PNG only and must be under 5MB"
                                      onChange={onFileUploadChanged}
                                      ></FileUpload>
                                    
                                    <div style={{display: imgData !== null ? "block" : "none"}}>
                                        <img  src={imgData} alt="document here" width= "600px" height="300px" />
                                    </div>
                                    
                                    <div style={{display: uploadedFile !== null ? "block" : "none"}}>
                                        <Button variant="primary"  onClick={identifyDocument} >
                                            Identify Document
                                        </Button>
                                        <Button  variant="link"  onClick={() => setVisible(true)}>View Image</Button>
                                    </div>
                                </Stack>
                            </Stack>
                        </Column>
                    <Column key="column2">
                        <TextractResponse data={wsResponse}/>    
                    </Column>
                </ColumnLayout>   
            </Container> 
            <Modal title={selectedImage} width="80%" visible={visible} onClose={() => setVisible(false)}>
                <img  src={imgData}  style={imageStyle} />
            </Modal>
        </div>
    );
};

export default DocumentTaker;
