# Augmented Image - Technical Documentation

## Overview
**Augmented Image** (also known as "Interactive Infographic Generator") is a dual-stage AI application. First, it generates a high-quality visual representation (infographic, diagram, or illustration) based on a user's abstract query. Then, it uses multimodal vision capabilities to "scan" that generated image, identify key regions of interest, and overlay interactive, data-rich widgets on top of it.

## Architecture

### File Structure
```
/
├── App.tsx                 # Main Controller (Search -> Generate -> Analyze -> Display)
├── components/
│   ├── AugmentedCanvas.tsx # The Rendering Engine (Image + Hitboxes)
│   ├── LoadingState.tsx    # "Scanning" Animation
│   └── widgets/
│       └── WidgetEngine.tsx # Dynamic Card Renderer (Stats, Actions, Details)
├── services/
│   └── geminiService.ts    # Dual-Client (Image Gen + Vision Analysis)
└── types.ts                # Data Models (Segment, BoundingBox, StatItem)
```

### Core Logic

#### 1. The Generation Pipeline (`App.tsx`)
The application defines a strict status machine:
1.  **`idle`**: Waiting for user input.
2.  **`generating`**: Calls `generateInfographic` to create the visual base.
3.  **`analyzing`**: Seamlessly transitions to `analyzeImageRegions`. The UI shows a "Scanning" overlay with phrases like "Synthesizing contextual widgets...".
4.  **`complete`**: Displays the interactive result.

#### 2. The Vision Analysis (`services/geminiService.ts`)
This is the unique technical differentiator. After generating the image, the app sends it *back* to Gemini with a prompt to:
> "Identify 3-5 key regions in this infographic. Return their bounding boxes (0-100%) and structured data (stats, icons, descriptions) for each."
The output is a JSON array of `Segment` objects, which allows the app to know *where* to place interactivity on a flat image it just created.

#### 3. AugmentedCanvas (The Interactive Layer)
-   **Hitbox Mapping**: Maps the percentage-based `bounds` from the AI response to absolute CSS positioning (`left: 50%, top: 20%`).
-   **Interaction**: Handles hover states. When a user hovers a region, it dims the background (`backdrop-blur`) and highlights the specific segment.
-   **Widget Engine**: Renders different UI cards based on the segment's `category`:
    -   `data`: Shows statistical bars/charts.
    -   `concept`: Shows a descriptive card with an icon.
    -   `process`: Shows a step-by-step list.

### AI Integration

#### Models
-   **Generation**: `imagen-3.0-generate-001` (via Gemini API) for high-fidelity visuals.
-   **Analysis**: `gemini-1.5-pro` (Vision) for understanding spatial layout and content.

#### Prompt Strategy
-   **Infographic Prompt**: "Create a clean, dark-mode, sci-fi style infographic about {query}. Use neon colors on black background." (Ensures visual consistency).
-   **Analysis Prompt**: "Return JSON. Find the most important distinct visual elements. Estimate their bounding box coordinates."

## Key Technical Features
1.  **Spatial Understanding**: The app effectively gives "buttons" to a flat image by asking the AI where the buttons should be.
2.  **Context-Aware UI**: The widgets aren't generic; they adapt their layout (Compact vs Detailed vs Stats) based on what the AI says is appropriate for that region.
3.  **Seamless Transition**: The "Scanning" phase masks the latency of the second AI call, making it feel like a single cohesive "Magic" process.
