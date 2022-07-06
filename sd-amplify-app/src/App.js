import MainContent from './components/MainContent'

import NorthStarThemeProvider from 'aws-northstar/components/NorthStarThemeProvider';
import { withAuthenticator} from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css'; // default theme

document.title = 'Swift Smart Document'

function App() {
  return (
    <div>
            <NorthStarThemeProvider>
              <MainContent/>
            </NorthStarThemeProvider>

        </div>
  );
}

export default withAuthenticator(App);