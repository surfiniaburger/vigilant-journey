# Augmented Canvas: Frontend Rendering Guide

This guide explains how the React frontend transforms raw backend JSON into an interactive, augmented reality-style interface.

## 1. User Journey

1.  **Input**: The user enters a vehicle query (e.g., "M139 Turbocharger") or clicks a suggestion.
2.  **Visuals**: The app generates a high-fidelity image locally (via client-side Gemini) to serve as the "canvas".
3.  **Analysis**: The app sends this image + query to the **Pilot Backend** (`/analyze`).
4.  **Streaming**: While waiting, the UI displays real-time logs ("Scanning...", "Routing to Alora...") via a 3D flipping text animation.
5.  **Result**: Once the JSON arrives, the UI enters "Augmented Mode", overlaying interactive hotspots on the image.

---

## 2. Rendering System

The rendering pipeline consists of three main components:

### A. State Management (`App.tsx`)
The root component holds the "Truth".
*   `data.image`: The raw base64 image.
*   `data.analysis`: The structured JSON from the backend (containing `segments`).

### B. The Canvas (`AugmentedCanvas.tsx`)
This component acts as the coordinate system. It renders the image and overlays **Hitboxes**.
*   **Coordinate mapping**: The backend returns `bounds` in percentages `{x: 45, y: 30, width: 20...}`.
*   **Absolute Positioning**: The canvas renders transparent `<div>` elements using these percentages: `left: 45%; top: 30%...`.
*   **Interactivity**: When a user **hovers** over a hitbox:
    1.  The hitbox glows (CSS borders/animations).
    2.  The background image blurs slightly to focus attention.
    3.  A "Modal" overlay is triggered with the specific Segment data.

### C. The Widget Engine (`WidgetEngine.tsx`)
This is a "Factory" component. It takes a raw `Segment` object and decides which **Card** to render based on the `format` field.

| Backend Format | Frontend Component | Visual Style |
| :--- | :--- | :--- |
| `"compact"` | `<CompactWidget>` | Glass panel with icon, title, and description. Standard view. |
| `"stats"` | `<StatsWidget>` | Grid layout focusing on numerical data (RPM, Bar, HP). |
| `"detailed"` | `<DetailedWidget>` | Full-width header, gradient backdrops, scrollable text. |
| `"mini"` | `<MiniWidget>` | Small capsule pill. Just icon + label. |

---

## 3. Data Flow Example

Dotted line shows how a single byte of data travels to pixels on the screen.

1.  **Backend JSON**:
    ```json
    { "label": "Turbo", "format": "stats", "stats": [{"label": "RPM", "value": "169k"}] }
    ```
    ⬇️
2.  **App.tsx** (State):
    Stores in `analysis.segments[0]`.
    ⬇️
3.  **AugmentedCanvas.tsx** (Hitbox):
    Renders hidden div at `bounds`. User hovers -> passes object to...
    ⬇️
4.  **WidgetEngine.tsx** (Factory):
    Reads `format="stats"`. Selects `<StatsWidget>`.
    ⬇️
5.  **StatsWidget** (Render):
    Maps over `stats` array. Renders "169k" in Cyan font.

## 4. Key UX Features
*   **Scanning Mode**: Before data arrives, a simulated "scanner" animation (moving gradient) plays over the image to imply processing.
*   **Ambience**: The layout uses global ambient background gradients (`purple-900/20`, `cyan-900/20`) to create a cohesive "Mercedes-Benz OS" feel.
*   **Animations**: All transitions (fade-ins, scale-ups) are handled by `framer-motion` for 60fps smoothness.
