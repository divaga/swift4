import React, {useState} from 'react';
import AppLayout from 'aws-northstar/layouts/AppLayout';
import Box from 'aws-northstar/layouts/Box';
import Header from 'aws-northstar/components/Header';
import Button from 'aws-northstar/components/Button';
import SideNavigation, {SideNavigationItemType} from 'aws-northstar/components/SideNavigation';
import HelpPanel from 'aws-northstar/components/HelpPanel';
import Link from 'aws-northstar/components/Link';
import Text from 'aws-northstar/components/Text';
import Heading from 'aws-northstar/components/Heading';
import {Switch} from "react-router-dom";
import {MemoryRouter, Route} from 'react-router';
import DocumentTaker from "../DocumentImageTaker";
import DocumentationContent from "../DocumentationContent"
import { Auth } from 'aws-amplify';

function MainContent() {
    
    const handleLogout = async function() {
    try {
        await Auth.signOut();
    } catch (error) {
        console.log('error signing out: ', error);
    }
   };
   

    const header = <Header title='Swift Smart Document Demo ' rightContent={<Button onClick={handleLogout} variant="primary">Logout</Button>}/>;
    const navigationItems = [
        {type: SideNavigationItemType.LINK, text: 'Home', href: '/'},
        {type: SideNavigationItemType.LINK, text: 'Documentation', href: '/docs'},
        
        {
            type: SideNavigationItemType.LINK,
            text: 'User License',
            href: 'https://aws.amazon.com/asl/'
        },
        {
            type: SideNavigationItemType.LINK,
            text: 'AWS Website',
            href: 'https://aws.amazon.com',
        }
    ];

    const navigation = (
        <SideNavigation
            header={{
                href: '/',
                text: 'Smart Document Test Interface',
            }}
            items={navigationItems}
        />
    );
    const helpPanel = (
        <HelpPanel
            header="Help panel title (h2)"
            learnMoreFooter={[
                <Link key='internalDoc' href="/docs">Link to internal documentation</Link>,
                <Link key='externalDoc' href="https://www.yoursite.com">Link to external documentation</Link>,
            ]}
        >
            <Text variant="p">
                This is a paragraph with some <b>bold text</b> and also some <i>italic text.</i>
            </Text>
            <Heading variant="h4">h4 section header</Heading>
            <Heading variant="h5">h5 section header</Heading>
        </HelpPanel>
    );
    
    const mainContent = (
        /*<Box bgcolor="grey.300" width="100%" height="1000px">
           
        </Box>*/
        <DocumentTaker />
    );
   

    return (
        <MemoryRouter>

            <AppLayout
                header={header}
                navigation={navigation}
                >

                <Switch>
                    <Route path="/" exact={true}>
                        {mainContent}
                    </Route>
                    <Route path="/docs" component={DocumentationContent}/>
                </Switch>
            </AppLayout>
        </MemoryRouter>
    )
}

export default MainContent
