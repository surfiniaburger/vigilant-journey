/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// --- Datadog RUM Initialization ---
import { datadogRum } from '@datadog/browser-rum';

datadogRum.init({
  applicationId: '5dbfaf08-4635-42e2-8420-9d9e91592888',
  clientToken: 'pub86086537789c1572ddab92888b6fdad0',
  site: 'us5.datadoghq.com',
  service: 'pilot-frontend',
  env: 'production',
  // Specify a version number to identify the deployed version of your application in Datadog 
  // version: '1.0.0', 
  sessionSampleRate: 100,
  sessionReplaySampleRate: 20,
  trackUserInteractions: true,
  trackResources: true,
  trackLongTasks: true,
  defaultPrivacyLevel: 'mask-user-input',
});
// ----------------------------------

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
