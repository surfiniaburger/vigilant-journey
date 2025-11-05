"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { useIdToken } from "@/hooks/use-id-token"
import { useAudio } from "@/lib/use-audio"
import { Map } from "@/components/ui/map"
import { VoiceButton } from "@/components/ui/voice-button"
import { Response } from "@/components/ui/response"

interface MapCommand {
  action: "set_map_center"
  lat: number
  lng: number
}

export default function MapPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/")
    }
  }, [user, authLoading, router])

  const {
    idToken,
    loading: tokenLoading,
    error: tokenError,
  } = useIdToken({
    user,
    enabled: !!user,
  })

  // Initialize audio hook only when we have a token
  const { audioState, text, /*sendText,*/ startRecording, stopRecording } = useAudio(idToken)

  const [mapCenter, setMapCenter] = useState({ lat: 37.7704, lng: -122.3985 })
  const [agentResponse, setAgentResponse] = useState("")
  // const [inputValue, setInputValue] = useState("")

  const handleToggleRecording = useCallback(() => {
    if (audioState === "recording") {
      stopRecording()
    } else {
      setAgentResponse("")
      startRecording()
    }
  }, [audioState, startRecording, stopRecording])

  // const handleTextSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  //   e.preventDefault()
  //   if (inputValue.trim()) {
  //     sendText(inputValue)
  //     setInputValue("")
  //   }
  // }

  // or use useCallback if it needs access to component state
  const isJsonString = useCallback((str: string): boolean => {
    if (!str?.trim().startsWith("{")) return false
    try {
      JSON.parse(str)
      return true
    } catch {
      return false
    }
  }, [])

  useEffect(() => {
    if (!text) return

    if (isJsonString(text)) {
      try {
        const command: MapCommand = JSON.parse(text)
        if (command.action === "set_map_center") {
          setMapCenter({ lat: command.lat, lng: command.lng })
          setAgentResponse("Panning map to new location.")
          return
        }
      } catch (err) {
        console.error("[v0] Failed to parse command:", err)
        // Fall through to treat as regular response
      }
    } else if (text.trim().startsWith("{")) {
      try {
        JSON.parse(text)
      } catch (err) {
        console.error("[v0] Failed to parse command:", err)
      }
    }
    setAgentResponse(text)
  }, [text, isJsonString])

  if (tokenError) {
    return (
      <div className="w-full h-screen flex flex-col items-center justify-center bg-background gap-4">
        <div className="text-destructive text-lg font-semibold">Authentication Error</div>
        <p className="text-muted-foreground text-sm max-w-md text-center">{tokenError.message}</p>
        <button onClick={() => router.push("/")} className="text-sm text-primary hover:underline">
          Return to Home
        </button>
      </div>
    )
  }

  if (authLoading || tokenLoading || !user || !idToken) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-muted border-t-foreground" />
          <p className="text-muted-foreground text-sm">Authenticating...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-screen relative">
      <Map center={mapCenter} />

      {agentResponse && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/50 backdrop-blur-sm text-white p-4 rounded-lg max-w-md shadow-lg animate-in fade-in-50">
          <Response>{agentResponse}</Response>
        </div>
      )}

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2">
        {/* <form onSubmit={handleTextSubmit} className="flex items-center gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="w-full px-4 py-2 text-white bg-black/50 border border-white/20 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type a message..."
          />
          <button
            type="submit"
            className="px-4 py-2 text-white bg-blue-500 rounded-full hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Send
          </button>
        </form> */}
        <VoiceButton
          state={audioState === "recording" ? "recording" : "idle"}
          onPress={handleToggleRecording}
          size="icon"
          className="w-16 h-16"
        />
      </div>
    </div>
  )
}
