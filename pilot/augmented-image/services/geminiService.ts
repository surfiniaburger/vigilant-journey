/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import { AnalysisResult, GeneratedImage } from "../types";

// Detect backend URL (Cloud Run or Local)
// Ideally this should be in an env var, but for this POC we'll use a relative path if served from same origin, or default
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8080';

export const generateInfographic = async (query: string): Promise<GeneratedImage> => {
  // NOTE: For generating the INITIAL image, we might still want to use the client-side SDK
  // OR we can route this through the backend too if we want.
  // The user request specifically mentioned "analyze image", so let's stick to the analysis part through the backend first.
  // However, keeping two different auth methods is messy.
  // Let's assume for this step we keep image generation client-side (as it's just for the "visual"),
  // and the ANALYSIS (the important part) goes through the Pilot.
  // Wait, the user said "where to easily call the pilot endpoint... so that the result... would then be used".
  // Let's keep generation here for now to minimize disruption, but point Analysis to Pilot.

  // Actually, to be "safe", we should probably move generation to backend too, 
  // but the backend agent is "Search Agent", not "Image Generation Agent".
  // So I will leave this as is (Client Side) for the Visuals, and use Pilot for Truth.

  const { GoogleGenAI } = await import("@google/genai");
  const ai = new GoogleGenAI({ apiKey: import.meta.env.VITE_API_KEY }); // Still need API key for generation

  const prompt = `
Create an explanation-driven, sparse-text, rich image about: "${query}"

IMPORTANT STYLE GUIDELINES:
- Create a diagram or infographic but with minimal text - keep it visually focused
- Focus on compelling imagery, scenes, objects, or artistic representations
- Use dramatic lighting, rich colors, and cinematic composition
- Think editorial photography or concept art, not charts or diagrams
- The image should be atmospheric and immersive

Generate a stunning visual that captures the essence of the topic through imagery, not words.`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: prompt,
      config: {
        imageConfig: {
          aspectRatio: '16:9'
        }
      },
    });

    // Extract Image - Standard Gemini 2.x extraction
    let imageBase64: string | undefined;
    let mimeType = 'image/png';
    const parts = response.candidates?.[0]?.content?.parts;

    if (parts) {
      for (const part of parts) {
        if (part.inlineData) {
          imageBase64 = part.inlineData.data;
          mimeType = part.inlineData.mimeType || 'image/png';
          break;
        }
      }
    }

    if (!imageBase64) throw new Error("No image generated.");

    return { base64: imageBase64, mimeType, groundingUrls: [] };

  } catch (error) {
    console.error("Image Generation Error:", error);
    throw error;
  }
};

export const analyzeImageRegions = async (query: string, imageBase64: string): Promise<AnalysisResult> => {

  console.log(`Sending analysis request to Pilot: ${BACKEND_URL}/analyze`);

  const prompt = `
Analyze this image about "${query}" and identify interesting regions to annotate.
Verify facts using your internal research tools.

Identify 4-6 distinct visual areas in the image. For each area, provide widget data.

CRITICAL CONTENT GUIDELINES:
- **RICH DESCRIPTIONS:** Do not write one-liners. Descriptions must be 2-3 sentences, immersive, and educational. Explain *why* this part matters.
- **ICONS:** "icon" must be a SINGLE valid Emoji.
- **TONE:** Scientific, futuristic, yet accessible. 
- **FORMATS:** Use "compact", "stats", or "detailed".

Provide this data:
- "label": Name (1-4 words)
- "format": "compact" | "stats" | "detailed"
- "description": Rich text (approx 30-50 words).
- "category": "concept" | "data" | "process" | "structure"
- "icon": A single relevant emoji.
- "stats": Array of facts (ONLY for stats/detailed formats) { "label", "value" }
- "sourceUrl": A relevant Wikipedia or educational URL found via search.
- "sourceName": Short name for the source.
- "bounds": { "x": number (0-100), "y": number (0-100), "width": number (0-100), "height": number (0-100) }

Mix formats. Ensure the "bounds" accurately target specific visual elements in the image.

Return ONLY valid JSON. DO NOT CHAT. DO NOT ADD MARKDOWN formatting:
{
  "segments": [ ... ]
}`;

  try {
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: prompt,
        image: imageBase64,
        mime_type: "image/png"
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Pilot Backend Error (${response.status}): ${errorText}`);
    }

    const data = await response.json();
    const text = data.text;

    if (!text) throw new Error("No analysis received from Pilot.");

    // Helper to robustly extract the first valid JSON object
    const extractJSON = (str: string): any => {
      const startIndex = str.indexOf('{');
      if (startIndex === -1) throw new Error("No JSON object found");

      let braceCount = 0;
      let endIndex = -1;

      for (let i = startIndex; i < str.length; i++) {
        if (str[i] === '{') braceCount++;
        else if (str[i] === '}') {
          braceCount--;
          if (braceCount === 0) {
            endIndex = i;
            break;
          }
        }
      }

      if (endIndex === -1) throw new Error("Malformed JSON: No closing brace");

      const jsonStr = str.substring(startIndex, endIndex + 1);
      return JSON.parse(jsonStr);
    };

    return extractJSON(text) as AnalysisResult;

  } catch (error) {
    console.error("Pilot Analysis Error:", error);
    throw error;
  }
};