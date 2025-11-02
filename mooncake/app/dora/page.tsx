"use client"

import { useEffect, useState, useCallback, useRef, createElement } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { useIdToken } from "@/hooks/use-id-token"
import { Map } from "@/components/ui/map"
import { Response } from "@/components/ui/response"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface MapCommand {
  action: "set_map_center"
  lat: number
  lng: number
}

export default function DoraPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  // const mapRef = useRef<any>(null)
  const placeSearchRef = useRef<HTMLElement | null>(null)
  const placeDetailsRef = useRef<HTMLElement | null>(null)

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

  const [mapCenter, setMapCenter] = useState({ lat: 37.7704, lng: -122.3985 })
  const [agentResponse, setAgentResponse] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [text, setText] = useState("")
  const [selectedPlace, setSelectedPlace] = useState<{ place?: unknown } | null>(null)

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return
    console.log("Sending message:", inputValue)

    const requestBody = {
      app_name: "dora",
      user_id: user?.uid || "anonymous",
      session_id: "dora-session",
      new_message: {
        role: "user",
        parts: [{ text: inputValue }],
      },
    }

    try {
      console.log("Calling /api/agent with body:", requestBody)
      const response = await fetch("/api/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      console.log("Received response from /api/agent:", response)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("Parsed response data:", data)
      const lastEvent = data[data.length - 1]
      if (lastEvent && lastEvent.content && lastEvent.content.parts) {
        const responseText = lastEvent.content.parts[0].text
        console.log("Setting text from agent response:", responseText)
        setText(responseText)
      }
    } catch (error) {
      console.error("Failed to send message to agent:", error)
      setAgentResponse("Sorry, I couldn't connect to the agent.")
    }

    setInputValue("")
  }

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
      }
    }
    setAgentResponse(text)
    setText("")
  }, [text, isJsonString])

  useEffect(() => {
    const placeSearchElement = placeSearchRef.current
    const handlePlaceSelect = (event: Event & { place?: unknown }) => {
      setSelectedPlace(event as { place?: unknown })
    }
    if (placeSearchElement) {
      placeSearchElement.addEventListener("gmp-select", handlePlaceSelect)
    }
    return () => {
      if (placeSearchElement) {
        placeSearchElement.removeEventListener("gmp-select", handlePlaceSelect)
      }
    }
  }, [])

  useEffect(() => {
    if (placeDetailsRef.current && selectedPlace) {
      ;(placeDetailsRef.current as unknown as { place: unknown }).place = (selectedPlace as { place?: unknown }).place
    }
  }, [selectedPlace])

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

      <div className="absolute top-10 left-10 bg-white p-4 rounded-lg shadow-lg z-10">
        {createElement(
          'gmp-place-search',
          { ref: placeSearchRef, orientation: "vertical", selectable: true },
          createElement('gmp-place-all-content', null, ' '),
          createElement('gmp-place-text-search-request')
        )}
      </div>

      {selectedPlace && (
        <div className="absolute top-10 right-10 bg-white p-4 rounded-lg shadow-lg z-10">
          {createElement(
            'gmp-place-details-compact',
            { ref: placeDetailsRef, orientation: "horizontal" },
            createElement('gmp-place-details-place-request'),
            createElement('gmp-place-all-content')
          )}
        </div>
      )}

      {agentResponse && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/50 backdrop-blur-sm text-white p-4 rounded-lg max-w-md shadow-lg animate-in fade-in-50">
          <Response>{agentResponse}</Response>
        </div>
      )}

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-md flex items-center space-x-2 p-4">
        <Textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Send a message to Alora..."
          className="flex-1"
        />
        <Button onClick={handleSendMessage}>Send</Button>
      </div>
    </div>
  )
}
