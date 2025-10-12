const { TextEncoder, TextDecoder } = require('util');

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

document.body.innerHTML = `
  <div id="messages"></div>
  <form id="messageForm">
    <input id="message" />
    <button id="sendButton"></button>
  </form>
  <button id="startAudioButton"></button>
`;
