import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import Amplify from "aws-amplify";
import awsExports from "./aws-exports";
Amplify.configure(awsExports);
/*
Amplify.configure({
    API: {
        endpoints: [
            {
                name: 'SmartDocApi',
                endpoint: 'https://a6m7sigzk1.execute-api.ap-southeast-1.amazonaws.com/dev',
                region: 'ap-southeast-1'
            }
        ]
    }
});*/
ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
