# Pilot API Schema Documentation

This document describes the contract between the **Pilot Backend** (`pilot/main.py`) and the **Augmented Canvas Frontend** (`pilot/augmented-image/services/geminiService.ts`).

## Endpoint: `POST /analyze`

Orchestrates a full AI analysis session, including streaming thought logs and a final structured result.

### Request
*   **Content-Type**: `application/json`
*   **Body**:
    ```json
    {
      "text": "Analyze the suspension system in this image...",
      "image": "base64_encoded_string_without_header..."
    }
    ```

### Response (Streaming)

The endpoint uses **Server-Sent Events (SSE)** style formatting (specifically NDJSON/lines) over a standard HTTP response stream to provide real-time feedback.

The stream yields JSON objects, one per line. Each object can be one of two types: **Log** or **Result**.

#### 1. Log Event (Streamed during execution)
Used to display the agent's thought process in the UI "toast" or console.

```json
{
  "log": "🤖 Orchestrating Workflow..."
}
```

#### 2. Result Event (Final Output)
Emitted once at the very end of the stream. Contains the structured data payload.

```json
{
  "result": {
    "text": "JSON_STRING_HERE"
  }
}
```

> **Note**: The `text` field usually contains a JSON string that must be parsed by the client. This wrapper exists because the Agent framework outputs "text" content types.

---

## Data Model (Analysis Result)

Once the client parses the `result.text` JSON string, it matches the following TypeScript interface:

### `AnalysisResult`
The root object returned by the analysis.

```json
{
  "segments": [
    {
      "label": "M139 Turbocharger",
      "format": "detailed",
      "description": "Twin-scroll turbocharger capable of 169,000 RPM...",
      "category": "structure",
      "icon": "🐌",
      "bounds": {
        "x": 45,
        "y": 30,
        "width": 20,
        "height": 25
      },
      "stats": [
        { "label": "Max RPM", "value": "169k" },
        { "label": "Pressure", "value": "2.1 bar" }
      ],
      "sourceUrl": "https://en.wikipedia.org/wiki/Mercedes-Benz_M139_engine",
      "sourceName": "Wikipedia"
    }
  ]
}
```

---

## Field Definitions

### `Segment` Object

| Field | Type | Description |
| :--- | :--- | :--- |
| `label` | `string` | Short title of the identified region (1-4 words). |
| `format` | `enum` | Visualization style: `"compact"`, `"stats"`, `"detailed"`, `"mini"`. |
| `description` | `string` | Rich text explaining the component's function or significance (30-50 words). |
| `category` | `enum` | Semantic type: `"concept"`, `"data"`, `"process"`, `"structure"`, `"highlight"`, `"detail"`, `"context"`. |
| `icon` | `string` | Single emoji character representing the item. |
| `bounds` | `object` | Relative coordinates (0-100%) for the UI overlay box: `{x, y, width, height}`. |
| `stats` | `array` | Optional list of key-value pairs (see below). |
| `sourceUrl` | `string` | URL to the source of the fact (grounding). |
| `sourceName` | `string` | Display name of the source (e.g., "Wikipedia"). |

### `StatItem` Object (Inside `stats` array)

| Field | Type | Description |
| :--- | :--- | :--- |
| `label` | `string` | Metric name (e.g., "Max Speed"). |
| `value` | `string` | Metric value (e.g., "200 mph"). |
| `icon` | `string` | Optional emoji for the specific stat. |
