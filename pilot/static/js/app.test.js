/**
 * @jest-environment jsdom
 */

import { base64ToArray, arrayBufferToBase64, audioRecorderHandler, sendBufferedAudio, stopAudioRecording } from './app.js';

describe('Base64 and ArrayBuffer conversions', () => {

  // Test case for arrayBufferToBase64
  test('arrayBufferToBase64 should correctly encode an ArrayBuffer to Base64', () => {
    const text = "Hello, World!";
    const encoder = new TextEncoder();
    const arrayBuffer = encoder.encode(text).buffer;
    const expectedBase64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
    expect(arrayBufferToBase64(arrayBuffer)).toBe(expectedBase64);
  });

  // Test case for base64ToArray
  test('base64ToArray should correctly decode a Base64 string to an ArrayBuffer', () => {
    const text = "Hello, Jest!";
    const base64 = btoa(text);
    const expectedArray = new Uint8Array(text.split('').map(char => char.charCodeAt(0))).buffer;
    const decodedArrayBuffer = base64ToArray(base64);

    // Compare ArrayBuffers by converting them to Uint8Arrays and then to strings
    const decodedString = new TextDecoder().decode(decodedArrayBuffer);
    expect(decodedString).toBe(text);
  });

  test('base64ToArray should handle empty string', () => {
    const base64 = "";
    const expectedArray = new Uint8Array(0).buffer;
    const decodedArrayBuffer = base64ToArray(base64);
    expect(decodedArrayBuffer.byteLength).toBe(expectedArray.byteLength);
  });

  test('arrayBufferToBase64 should handle empty ArrayBuffer', () => {
    const arrayBuffer = new Uint8Array(0).buffer;
    expect(arrayBufferToBase64(arrayBuffer)).toBe("");
  });

});

describe('Audio Handling', () => {
  let sendMessage;

  beforeEach(() => {
    // Clear mocks and timers before each test
    jest.useFakeTimers();
    sendMessage = jest.fn();
  });

  afterEach(() => {
    // Restore real timers
    jest.useRealTimers();
  });

  test('audioRecorderHandler should buffer audio data and send it after 200ms', () => {
    // Initial pcmData
    const pcmData = new ArrayBuffer(10);

    // Call the handler
    audioRecorderHandler(pcmData, sendMessage);

    // Fast-forward time by 200ms
    jest.advanceTimersByTime(200);

    // Check if sendMessage was called
    expect(sendMessage).toHaveBeenCalledTimes(1);
  });

  test('sendBufferedAudio should not send empty buffer', () => {
    // Call sendBufferedAudio without any data in the buffer
    sendBufferedAudio(sendMessage);

    // Check that sendMessage was not called
    expect(sendMessage).not.toHaveBeenCalled();
  });

  test('stopAudioRecording should clear the buffer and interval', () => {
    // Initial pcmData
    const pcmData = new ArrayBuffer(10);

    // Call the handler
    audioRecorderHandler(pcmData, sendMessage);

    // Stop the recording
    stopAudioRecording();

    // Fast-forward time by 200ms
    jest.advanceTimersByTime(200);

    // Check that sendMessage was not called after stopping
    expect(sendMessage).not.toHaveBeenCalled();
  });
});