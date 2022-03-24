import React from "react";
import Container from 'aws-northstar/layouts/Container';
import Stack from "aws-northstar/layouts/Stack";
import Heading from 'aws-northstar/components/Heading';
import Text from 'aws-northstar/components/Text';
import Link from 'aws-northstar/components/Link';
import Table from 'aws-northstar/components/Table';
import { content } from './content'

function DocumentationContent() {
     
     const ArchitectureContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Architecture</Heading>
                    <Text variant='p'>{content.architecture.text}</Text>
                    <img  src={process.env.PUBLIC_URL+'swift-architecture-noflow.png'} alt="architecture" width= "600px" height="300px" />
                </Stack>
            )
    }
    
    const ArchitectureFlowContent = () =>{
        const columnDefinitions = [
            {
                id: 'id',
                width: 100,
                Header: 'Sequence',
                accessor: 'seq'
            },
            {
                id: 'description',
                width: 800,
                Header: 'Description',
                accessor: 'text'
            }]
            
        return(
                <Stack>
                    <Heading variant='h4'>Application Flow</Heading>
                    <Text variant='p'>{content.appflow.text}</Text>
                    <img  src={process.env.PUBLIC_URL+'swift-architecture-flow.png'} alt="architecture" width= "600px" height="300px" />
                    <Table
                        onSelectionChange={()=> {}}
                        tableTitle='Application Flow'
                        columnDefinitions={columnDefinitions}
                        items={content.appflow.flows}
                        disableGroupBy={true}
                        disableSettings={true}
                        disablePagination={false}
                        disableFilters={true}
                        disableRowSelect={true}
                        disableSortBy={true}
                    />
                </Stack>
            )
    }
    
    const AdvanceFeaturesContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Features</Heading>
                    <Text variant='p'>{content.features.text}</Text>
                    <Stack spacing='none'>
                        <Text variant='span'>{content.features.details[0]}</Text>
                        <Text variant='span'>{content.features.details[1]}</Text>
                        <Text variant='span'>{content.features.details[2]}</Text>
                        <Text variant='span'>{content.features.details[3]}</Text>
                        <Text variant='span'>{content.features.details[4]}</Text>
                    </Stack>
                </Stack>
            )
    }
    
    
    const UsageContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Usage</Heading>
                    <Text variant='p'>{content.usage.text}</Text>
                    <Stack spacing='none'>
                        <Text variant='span'>{content.usage.details[0]}</Text>
                        <Text variant='span'>{content.usage.details[1]}</Text>
                        <Text variant='span'>{content.usage.details[2]}</Text>
                    </Stack>
                </Stack>
            )
    }
    
    const OverviewContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Functional Overview</Heading>
                    <Text variant='p'>{content.overview} </Text>
                </Stack>
            )
    }
    
    const DocImageClassificationContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Document Image Classification</Heading>
                    <Text variant='p'>{content.imageclasssification.text} </Text>
                </Stack>
            )
    }
    
    const DocTextClassificationContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Document Text Classification</Heading>
                    <Text variant='p'>{content.textclassification.text} </Text>
                </Stack>
            )
    }
    
    const ResourceContent = () =>{
        return(
                <Stack>
                    <Heading variant='h4'>Resources</Heading>
                    <Text variant='p'>{content.resources.text} </Text>
                    <Link href={content.resources.link}>{content.resources.link}</Link>
                </Stack>
            )
    }

     return (
          <Container headingVariant='h2' title='Documentation' >
               <Stack>
                    <OverviewContent />
                    <AdvanceFeaturesContent />
                    <UsageContent />
                    <DocImageClassificationContent/>
                    <DocTextClassificationContent/>
                    <ArchitectureContent/>
                    <ArchitectureFlowContent/>
                    <ResourceContent/>
               </Stack>
          </Container>
     );     
    
}   

export default DocumentationContent;