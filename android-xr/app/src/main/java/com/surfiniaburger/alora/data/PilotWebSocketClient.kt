package com.surfiniaburger.alora.data

import android.util.Log
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PilotWebSocketClient @Inject constructor() {

    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS) // Keep the connection alive
        .build()

    private var webSocket: WebSocket? = null
    
    // Using a Channel to emit events to the ViewModel
    private val _events = Channel<PilotEvent>(Channel.BUFFERED)
    val events: Flow<PilotEvent> = _events.receiveAsFlow()

    fun connect(url: String) {
        val request = Request.Builder()
            .url(url)
            .build()
        
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d(TAG, "Connected to Pilot")
                trySend(PilotEvent.Connected)
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                Log.d(TAG, "Received message: $text")
                trySend(PilotEvent.Message(text))
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "Closing: $code / $reason")
                trySend(PilotEvent.Disconnected)
                webSocket.close(1000, null)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "Error: ${t.message}", t)
                trySend(PilotEvent.Error(t))
            }
        })
    }

    fun send(text: String) {
        webSocket?.send(text)
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
    }

    private fun trySend(event: PilotEvent) {
        _events.trySend(event).isSuccess
    }

    companion object {
        private const val TAG = "PilotWebSocketClient"
    }
}

sealed class PilotEvent {
    object Connected : PilotEvent()
    object Disconnected : PilotEvent()
    data class Message(val content: String) : PilotEvent()
    data class Error(val throwable: Throwable) : PilotEvent()
}
