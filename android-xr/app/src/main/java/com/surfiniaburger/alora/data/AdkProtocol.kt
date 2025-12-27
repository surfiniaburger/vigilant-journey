package com.surfiniaburger.alora.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AdkMessage(
    @SerialName("server_content") val serverContent: ServerContent? = null,
    @SerialName("realtime_input") val realtimeInput: RealtimeInput? = null
)

@Serializable
data class ServerContent(
    @SerialName("model_turn") val modelTurn: ModelTurn? = null
)

@Serializable
data class ModelTurn(
    val parts: List<Part> = emptyList()
)

@Serializable
data class Part(
    val text: String? = null,
    @SerialName("function_call") val functionCall: FunctionCall? = null,
    @SerialName("inline_data") val inlineData: InlineData? = null
)

@Serializable
data class FunctionCall(
    val name: String,
    val args: Map<String, kotlinx.serialization.json.JsonElement>? = null
)

@Serializable
data class InlineData(
    @SerialName("mime_type") val mimeType: String,
    val data: String // Base64 PCM
)

@Serializable
data class RealtimeInput(
    @SerialName("media_chunks") val mediaChunks: List<MediaChunk> = emptyList()
)

@Serializable
data class MediaChunk(
    @SerialName("mime_type") val mimeType: String,
    val data: String // Base64 PCM
)
