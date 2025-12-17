/*
 * Copyright 2025 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.surfiniaburger.alora.ui

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.util.Log
import androidx.annotation.RequiresPermission
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.surfiniaburger.alora.data.AudioStreamer
import com.surfiniaburger.alora.data.MicControl
import com.surfiniaburger.alora.data.PilotEvent
import com.surfiniaburger.alora.data.PilotWebSocketClient
import com.surfiniaburger.alora.data.Todo
import com.surfiniaburger.alora.data.TodoRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.lang.ref.WeakReference
import javax.inject.Inject

private const val MIC_TODO_ID = 111
private const val MIC_STATUS_TODO_ID = -999
private const val PILOT_BACKEND_URL = "wss://pilot-v1-684569726907.us-central1.run.app/ws/android-xr" // Placeholder endpoint

@HiltViewModel
class TodoScreenViewModel @Inject constructor(
    private val todoRepository: TodoRepository,
    private val pilotClient: PilotWebSocketClient,
    private val audioStreamer: AudioStreamer
) : ViewModel() {
    private val TAG = "TodoScreenViewModel"
    private var hostActivityRef: WeakReference<Activity>? = null

    private val liveSessionState = MutableStateFlow<LiveSessionState>(LiveSessionState.NotReady)
    private val todos = todoRepository.todos

    val uiState: StateFlow<TodoScreenUiState> = combine(liveSessionState, todos) { liveSessionState, currentTodos ->
        val micItem = currentTodos.filterIsInstance<MicControl>().firstOrNull()
        val isMicOn = micItem?.isMicOn ?: false

        val todoItems = currentTodos
            .filterIsInstance<Todo>()
            .filterNot { it.id == MIC_STATUS_TODO_ID }
            .reversed()

        TodoScreenUiState.Success(
            todoItems = todoItems,
            isMicOn = isMicOn,
            liveSessionState = liveSessionState
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000L),
        initialValue = TodoScreenUiState.Initial,
    )

    init {
        // Listen for Pilot events
        viewModelScope.launch {
            pilotClient.events.collect { event ->
                when (event) {
                    is PilotEvent.Connected -> {
                        Log.i(TAG, "Pilot: Connected")
                        liveSessionState.update { LiveSessionState.Ready }
                        todoRepository.updateMicStatus(micIsOn = false)
                    }
                    is PilotEvent.Disconnected -> {
                        Log.i(TAG, "Pilot: Disconnected")
                        liveSessionState.update { LiveSessionState.NotReady }
                        todoRepository.updateMicStatus(micIsOn = false)
                        audioStreamer.stopRecording()
                        audioStreamer.stopPlayback()
                    }
                    is PilotEvent.Error -> {
                        Log.e(TAG, "Pilot: Error", event.throwable)
                        liveSessionState.update { LiveSessionState.Error }
                        todoRepository.updateMicStatus(micIsOn = false)
                    }
                    is PilotEvent.Message -> {
                        // Log.d(TAG, "Pilot: Received ${event.content}")
                        handlePilotMessage(event.content)
                    }
                }
            }
        }
    }
    
    // Primitive parsing for now - in production use a real JSON parser or Protobuf
    private fun handlePilotMessage(text: String) {
        if (text.contains("\"audio\"")) {
            // Handle audio message: {"audio": "base64..."}
            try {
                // This is a very rough mock for parsing JSON without a full library dependency here if possible
                // Otherwise we should use proper serialization. For now let's assume valid JSON.
                // Or better, let's treat binary audio differently if we can. 
                // Since this is text, we'll need to optimize.
                // TODO: Implement proper Base64 decoding and audio queuing
                // audioStreamer.queueAudio(decodedBytes)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to parse audio message", e)
            }
        }
    }

    fun addTodo(taskDescription: String) {
        todoRepository.addTodo(taskDescription)
    }

    fun removeTodo(todoId: Int) {
        if (todoId == MIC_TODO_ID || todoId == MIC_STATUS_TODO_ID) return
        todoRepository.removeTodo(todoId)
    }

    fun toggleTodoStatus(todoId: Int) {
        if (todoId == MIC_TODO_ID) {
            todoRepository.toggleTodoStatus(MIC_TODO_ID)
            return
        }
        if (todoId == MIC_STATUS_TODO_ID) return
        todoRepository.toggleTodoStatus(todoId)
    }

    @RequiresPermission(Manifest.permission.RECORD_AUDIO)
    private fun startLiveSession() {
        val activity = hostActivityRef?.get() ?: run {
            Log.e(TAG, "Cannot start Pilot Session: Host Activity reference lost.")
            todoRepository.updateMicStatus(micIsOn = false)
            return
        }

        if (ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.RECORD_AUDIO,
            ) == PackageManager.PERMISSION_GRANTED
        ) {
            liveSessionState.update { LiveSessionState.Running }
            Log.i(TAG, "Pilot: Session Started (Streaming Audio)")
            
            // Start recording and sending
            viewModelScope.launch {
                audioStreamer.startRecording().collect { pcmData ->
                    // Normalize or Encode to Base64 before sending?
                    // Pilot v1 expects Base64 encoded audio in a JSON envelope? 
                    // Or raw binary? Let's assume binary for efficiency if WS supports it,
                    // but PilotClient sends text. We need Base64.
                    val base64Audio = android.util.Base64.encodeToString(pcmData, android.util.Base64.NO_WRAP)
                    pilotClient.send("{\"realtime_input\": {\"media_chunks\": [{\"mime_type\": \"audio/pcm\", \"data\": \"$base64Audio\"}]}}")
                }
            }
            
        } else {
            requestAudioPermissionIfNeeded(activity)
            todoRepository.updateMicStatus(micIsOn = false)
        }
    }

    private fun stopLiveSession() {
        if (liveSessionState.value is LiveSessionState.Running) {
            liveSessionState.update { LiveSessionState.Ready }
            Log.i(TAG, "Pilot: Session Stopped")
            audioStreamer.stopRecording()
        }
    }

    fun toggleLiveSession(activity: Activity) {
        todoRepository.toggleTodoStatus(MIC_TODO_ID)
    }

    fun initializeGeminiLive(activity: Activity) {
        hostActivityRef = WeakReference(activity)
        requestAudioPermissionIfNeeded(activity)

        viewModelScope.launch {
            todoRepository.todos.collect { todos ->
                val isMicOnInUI = todos.find { it.id == MIC_TODO_ID }
                    ?.let { it as? MicControl }?.isMicOn ?: false

                val currentLiveStatus = liveSessionState.value is LiveSessionState.Running

                if (isMicOnInUI != currentLiveStatus) {
                    if (isMicOnInUI) {
                        startLiveSession()
                    } else {
                        stopLiveSession()
                    }
                }
            }
        }
        
        // Connect to Pilot Backend
        Log.i(TAG, "Connecting to Pilot Backend...")
        pilotClient.connect(PILOT_BACKEND_URL)
    }

    fun requestAudioPermissionIfNeeded(activity: Activity) {
        if (ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.RECORD_AUDIO,
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(activity, arrayOf(Manifest.permission.RECORD_AUDIO), 1)
        }
    }
}