"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { useIdToken } from "@/hooks/use-id-token"
import { Response } from "@/components/ui/response"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface MapCommand {
  action: "set_map_center"
  lat: number
  lng: number
}

const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

export default function DoraPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [apiLoaded, setApiLoaded] = useState(false);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const placeSearchContainerRef = useRef<HTMLDivElement>(null);

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

  const [mapCenter, setMapCenter] = useState({ lat: 21.27655, lng: -157.82663 })
  const [agentResponse, setAgentResponse] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [text, setText] = useState("")

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !idToken) return
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
          "Authorization": `Bearer ${idToken}`,
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
    if (!GOOGLE_MAPS_API_KEY) {
      console.error("NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is not defined.");
      return;
    }

    const loadMapsApi = () => {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&v=beta&libraries=places,maps,marker,maps3d`;
      script.async = true;
      script.defer = true;
      script.onload = () => setApiLoaded(true);
      document.head.appendChild(script);
    };

    loadMapsApi();
  }, []);

  useEffect(() => {
    if (apiLoaded && mapContainerRef.current && placeSearchContainerRef.current) {
      const initMap = async () => {
        const map3d = document.createElement('gmp-map-3d');
        map3d.setAttribute('center', `${mapCenter.lat},${mapCenter.lng}`);
        map3d.setAttribute('mode', 'satellite');
        map3d.setAttribute('range', '1500');
        map3d.setAttribute('tilt', '73');
        map3d.setAttribute('heading', '38');
        mapContainerRef.current!.innerHTML = '';
        mapContainerRef.current!.appendChild(map3d);

        const popover = document.createElement('gmp-popover');
        popover.setAttribute('altitude-mode', 'relative-to-mesh');
        map3d.appendChild(popover);

        const placeDetails = document.createElement('gmp-place-details-compact');
        popover.appendChild(placeDetails);

        const detailsRequest = document.createElement('gmp-place-details-place-request');
        placeDetails.appendChild(detailsRequest);

        const standardContent = document.createElement('gmp-place-standard-content');
        placeDetails.appendChild(standardContent);

        const placeSearch = document.createElement('gmp-place-search');
        placeSearch.setAttribute('selectable', 'true');
        placeSearchContainerRef.current!.innerHTML = '';
        placeSearchContainerRef.current!.appendChild(placeSearch);

        const allContent = document.createElement('gmp-place-all-content');
        placeSearch.appendChild(allContent);

        const nearbyRequest = document.createElement('gmp-place-nearby-search-request');
        nearbyRequest.setAttribute('max-result-count', '5');
        nearbyRequest.setAttribute('included-primary-types', 'electric_vehicle_charging_station');
        nearbyRequest.setAttribute('location-restriction', `1500@${mapCenter.lat},${mapCenter.lng}`);
        placeSearch.appendChild(nearbyRequest);

        await google.maps.importLibrary("places")
        const {Marker3DInteractiveElement, AltitudeMode} = await google.maps.importLibrary("maps3d");
        /* eslint-disable @typescript-eslint/no-explicit-any */ 
        const handleClick = (place: any) => {
          if (detailsRequest) {
            (detailsRequest as any).place = place.id;
          }
          if (popover) {
            (popover as any).positionAnchor = place.location;
            (popover as any).open = true;
          }
        }

        if (placeSearch) {
          placeSearch.addEventListener('gmp-load', (e: any) => {
            for (const place of e.target.places) {
              const marker = new Marker3DInteractiveElement({
                position: place.location,
                extruded: true,
                drawsWhenOccluded: true,
                altitudeMode: AltitudeMode.RELATIVE_TO_MESH
              })
              marker.addEventListener("gmp-click", () => handleClick(place))
              if (map3d) {
                map3d.append(marker);
              }
            }
          });

          placeSearch.addEventListener('gmp-select', ({place}: any) => handleClick(place));
        }
      }

      initMap();
    }
  }, [apiLoaded, mapCenter]);

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
    <>
      <style>
        {`
          #map-container {
            width: 100%;
            height: 100%;
          }
          #place-search-container {
            position: absolute;
            inset: 30px auto auto 30px;
            width: 400px;
          }
          gmp-place-search {
            --gmp-mat-font-title-medium: 400 12px / 14px Garamond;
            --gmp-mat-color-on-surface: #e37400;
          }
          gmp-popover {
            --gmp-popover-pixel-offset-y: -48px;
          }
          gmp-place-details-compact {
            width: 350px;
            --gmp-mat-color-on-surface: #e37400;
          }
        `}
      </style>
      <div className="w-full h-screen relative">
        <div id="map-container" ref={mapContainerRef}></div>
        <div id="place-search-container" ref={placeSearchContainerRef}></div>

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
    </>
  )
}

