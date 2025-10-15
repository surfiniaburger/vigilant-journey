class PCMPlayerProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.isPlaying = false;
    this.port.onmessage = (event) => {
      if (event.data.command === "endOfAudio") {
        this.isPlaying = false;
        this.buffer = [];
        return;
      }
      const pcmData = new Int16Array(event.data);
      this.buffer.push(...pcmData);
      if (!this.isPlaying) {
        this.isPlaying = true;
      }
    };
  }

  process(inputs, outputs) {
    if (!this.isPlaying) {
      return true;
    }

    const output = outputs[0];
    const channel = output[0];
    const bufferSize = channel.length;

    for (let i = 0; i < bufferSize; i++) {
      if (this.buffer.length > 0) {
        channel[i] = this.buffer.shift() / 32768.0;
      } else {
        channel[i] = 0;
      }
    }

    if (this.buffer.length === 0) {
      this.isPlaying = false;
    }

    return true;
  }
}

registerProcessor("pcm-player-processor", PCMPlayerProcessor);
