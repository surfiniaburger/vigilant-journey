package com.surfiniaburger.alora.data

import android.annotation.SuppressLint
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.io.InputStream
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.ln

@Singleton
class AudioStreamer @Inject constructor() {
    private val scope = CoroutineScope(Dispatchers.IO)
    private var recordJob: Job? = null
    private var playJob: Job? = null
    private val audioQueue = Channel<ByteArray>(Channel.UNLIMITED)
    private var audioRecord: AudioRecord? = null
    private var audioTrack: AudioTrack? = null

    // Standard Geminin/Pilot Audio Format: 16kHz, 16-bit, Mono (PCM)
    private val sampleRate = 16000 // 16kHz
    private val channelConfigIn = AudioFormat.CHANNEL_IN_MONO
    private val channelConfigOut = AudioFormat.CHANNEL_OUT_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    private val bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfigIn, audioFormat) * 2

    fun startRecording(): Flow<ByteArray> = flow {
        if (checkPermissions()) {
            try {
                audioRecord = AudioRecord(
                    MediaRecorder.AudioSource.MIC,
                    sampleRate,
                    channelConfigIn,
                    audioFormat,
                    bufferSize
                )

                if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                    Log.e(TAG, "AudioRecord initialization failed")
                    return@flow
                }

                audioRecord?.startRecording()
                Log.d(TAG, "Recording started")

                val buffer = ByteArray(bufferSize)
                while (currentCoroutineContext().isActive) {
                    val readResult = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (readResult > 0) {
                        // Calculate volume level for UI visualization (basic RMS)
                        val volume = calculateVolume(buffer, readResult)
                        // Emit audio data as base64 compatible byte array
                        emit(buffer.copyOfRange(0, readResult))
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error in recording loop", e)
            } finally {
                stopRecording()
            }
        }
    }.flowOn(Dispatchers.IO)

    private fun flow(block: suspend kotlinx.coroutines.flow.FlowCollector<ByteArray>.() -> Unit): Flow<ByteArray> {
        return kotlinx.coroutines.flow.flow(block)
    }

    fun stopRecording() {
        try {
            if (audioRecord?.recordingState == AudioRecord.RECORDSTATE_RECORDING) {
                audioRecord?.stop()
            }
            audioRecord?.release()
            audioRecord = null
            Log.d(TAG, "Recording stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping recording", e)
        }
    }

    fun startPlayback() {
        if (playJob?.isActive == true) return

        val minBufferSize = AudioTrack.getMinBufferSize(sampleRate, channelConfigOut, audioFormat)
        
        audioTrack = AudioTrack.Builder()
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(audioFormat)
                    .setSampleRate(sampleRate)
                    .setChannelMask(channelConfigOut)
                    .build()
            )
            .setBufferSizeInBytes(minBufferSize)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()

        audioTrack?.play()

        playJob = scope.launch {
            for (chunk in audioQueue) {
                audioTrack?.write(chunk, 0, chunk.size)
            }
        }
    }

    fun queueAudio(pcmData: ByteArray) {
        if (playJob?.isActive != true) {
            startPlayback()
        }
        audioQueue.trySend(pcmData)
    }

    fun stopPlayback() {
        playJob?.cancel()
        audioQueue.cancel() // Clear queue? or create new channel? 
        // Re-creating channel is safer for restart:
        // Note: For this simplex implementation, we'll just stop the track.
        try {
            audioTrack?.stop()
            audioTrack?.release()
            audioTrack = null
        } catch (e: Exception) {
             Log.e(TAG, "Error stopping playback", e)
        }
    }

    private fun checkPermissions(): Boolean {
        // Permissions are handled in ViewModel/Activity
        return true 
    }

    private fun calculateVolume(buffer: ByteArray, readSize: Int): Double {
        var sum = 0.0
        for (i in 0 until readSize step 2) {
            // Little-endian 16-bit PCM
            val sample = (buffer[i].toInt() and 0xFF) or (buffer[i+1].toInt() shl 8)
            sum += sample * sample
        }
        val rms = Math.sqrt(sum / (readSize / 2))
        return 20 * ln(rms)
    }

    companion object {
        private const val TAG = "AudioStreamer"
    }
}
