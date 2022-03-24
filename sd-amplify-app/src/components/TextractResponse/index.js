import React from "react";
import Stack from 'aws-northstar/layouts/Stack';
import Heading from 'aws-northstar/components/Heading';
import Inline from 'aws-northstar/layouts/Inline';
import Container from 'aws-northstar/layouts/Container';
import KeyValuePair from 'aws-northstar/components/KeyValuePair';
import Flashbar from 'aws-northstar/components/Flashbar';
import Table from 'aws-northstar/components/Table';

const TextractResponse = (props) => {
    
    
    
    const ImageClassifitionData = () => {
         console.log( ' Data for Image Classifition : ' +props.data)
         const { data } = props;
         const response = data && data.body!== undefined ?  JSON.parse(JSON.stringify(data.body.sagemaker_response.response)): undefined;
         const  docClass = response && response.document_image_classification !== undefined ?  response.document_image_classification: "NO AVAILABLE DATA";
         const  docConfidence = response && response.imageclassification_confidence !== undefined ?  response.imageclassification_confidence: "NO AVAILABLE DATA";
         
        
        return (
            <Container headingVariant='h2' title='Document Image Classification' >
                <Inline>
                    <KeyValuePair label= "Classification" value={docClass}></KeyValuePair>
                    <KeyValuePair label="Confidence" value={docConfidence}></KeyValuePair>
                </Inline>
            </Container>
        );
    }
    
    const TextClassifitionData = () => {
         console.log( ' Data for Image Classifition : ' +props.data)
         const { data } = props;
         const response = data && data.body!== undefined ?  JSON.parse(JSON.stringify(data.body.textract_response.response)): undefined;
         const  documenttype = response && response.document_type !== undefined ?  response.document_type: "NO AVAILABLE DATA";
         const  country = response && response.country !== undefined ?  response.country: "NO AVAILABLE DATA";
         
        
        return (
            <Container headingVariant='h2' title='Document Text Classification' >
                <Inline>
                    <KeyValuePair label= "Document Type" value={documenttype}></KeyValuePair>
                    <KeyValuePair label="Country" value={country}></KeyValuePair>
                </Inline>
            </Container>
        );
    }
    
    const DisplayData = (title) =>{
        console.log( ' DisplayData  : ' +props.data)
         const { data } = props;
         const response = data && data.body!== undefined ?  JSON.parse(JSON.stringify(data.body.textract_response.response)): undefined;
         var datalist =[];
         console.log(response);
         const columnDefinitions = [
            {
                id: 'field"',
                width: 200,
                Header: 'Field Name',
                accessor: 'field'
            },
            {
                id: 'value',
                width: 200,
                Header: 'Value',
                accessor: 'value'
            },
            {
                id: 'confidence',
                width: 200,
                Header: 'Confidence',
                accessor: 'confidence'
            }
        ];
    
         if(response !== undefined) {
             const keyval = response.key_values;
             Object.keys(keyval).forEach(function(key) {
                 const item = {
                     "field":key,
                     "value":keyval[key].values,
                     "confidence":keyval[key].confidence
                 }
                datalist.push(item);
            });
         }
         console.log(datalist);
        return(
                <div>
                    <Table
                        tableTitle="Extracted Text Data"
                        columnDefinitions={columnDefinitions}
                        items={datalist}
                        disableGroupBy={true}
                        disableSettings={true}
                        disablePagination={true}
                        disableFilters={true}
                        disableRowSelect={true}
                        disableSortBy={true}
                    />
                </div>
            )
    }
    
   
    const NoData = () =>{
        return(
                <div>
                    <Heading variant='h5'></Heading>
                </div>
            )
    }
    
    const TextractData = () => {
         console.log( ' Data for Text Analysis  : ' +props.data)
         const { data } = props;
    
         let content ={};
         const docClass = data && data.body!== undefined ?  data.body.sagemaker_response.response.document_image_classification : "NO AVAILABLE DATA";
        
        if(docClass.indexOf('DRIVER')>=0){
            content = DisplayData('Driver License Data');
        }else if(docClass.indexOf('PASSPORT')>=0){
            content = DisplayData('Passport Data');
        }else if(docClass.indexOf('CITIZEN')>=0){
            content = DisplayData('Citizen ID Data');
        }else{
            content = NoData();
        }
        
        return (
            <div>
                {content}
            </div>    
        );
    }
    
    return (    
       <div>
            <Stack spacing='s'>
                <Stack spacing='m'>
                    { props.data && props.data.wsStatus !== null ? <Flashbar items={props.data.wsStatus} /> : <br/>}
                </Stack>
                <ImageClassifitionData />
                <TextClassifitionData />
                <TextractData />
            </Stack>
      </div>
  );
};

export default TextractResponse