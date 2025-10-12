let micStream: MediaStream | null = null;
let audioContext: AudioContext | null = null;
let audioWorkletNode: AudioWorkletNode | null = null;

const convertFloat32ToPCM = (inputData: Float32Array): ArrayBuffer => {
  const pcm16 = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    pcm16[i] = inputData[i] * 0x7fff;
  }
  return pcm16.buffer;
};

export const startAudioRecording = async (
  audioRecorderHandler: (pcmData: ArrayBuffer) => void
) => {
  try {
    audioContext = new AudioContext({ sampleRate: 16000 });

    await audioContext.audioWorklet.addModule("/pcm-recorder-processor.js");

    micStream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1 },
    });

    const source = audioContext.createMediaStreamSource(micStream);
    audioWorkletNode = new AudioWorkletNode(
      audioContext,
      "pcm-recorder-processor"
    );

    source.connect(audioWorkletNode);

    audioWorkletNode.port.onmessage = (event) => {
      const pcmData = convertFloat32ToPCM(event.data);
      audioRecorderHandler(pcmData);
    };
  } catch (error) {
    console.error("Error starting audio recording:", error);
  }
};

export const stopAudioRecording = () => {
  if (micStream) {
    micStream.getTracks().forEach((track) => track.stop());
    micStream = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  if (audioWorkletNode) {
    audioWorkletNode.disconnect();
    audioWorkletNode = null;
  }
};
