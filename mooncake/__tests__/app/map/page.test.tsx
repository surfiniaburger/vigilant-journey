"use client"

import type React from "react"

import "@testing-library/jest-dom"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { useRouter } from "next/navigation"
import MapPage from "@/app/map/page"
import { useAuth } from "@/context/AuthContext"
import { useIdToken } from "@/hooks/use-id-token"
import { useAudio } from "@/lib/use-audio"

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}))

jest.mock("@/context/AuthContext", () => ({
  useAuth: jest.fn(),
}))

jest.mock("@/hooks/use-id-token", () => ({
  useIdToken: jest.fn(),
}))

jest.mock("@/lib/use-audio", () => ({
  useAudio: jest.fn(() => ({
    audioState: "idle",
    text: "",
    startRecording: jest.fn(),
    stopRecording: jest.fn(),
  })),
}))

jest.mock("@/components/ui/map", () => ({
  Map: ({ center }: { center: { lat: number; lng: number } }) => (
    <div data-testid="map-container" data-center={JSON.stringify(center)}>
      Map Component
    </div>
  ),
}))

jest.mock("@/components/ui/voice-button", () => ({
  VoiceButton: ({ state, onPress }: { state: string; onPress: () => void }) => (
    <button data-testid="voice-button" aria-pressed={state === "recording"} onClick={onPress}>
      {state === "recording" ? "Stop Recording" : "Start Recording"}
    </button>
  ),
}))

jest.mock("@/components/ui/response", () => ({
  Response: ({ children }: { children: React.ReactNode }) => <div data-testid="response-display">{children}</div>,
}))

describe("Map Page - Authenticated User Journey", () => {
  const mockPush = jest.fn()
  const mockGetIdToken = jest.fn()
  const mockStartRecording = jest.fn()
  const mockStopRecording = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  const mockUser = {
    uid: "test-user-123",
    email: "test@example.com",
    getIdToken: mockGetIdToken,
  }

  describe("Authentication & Token Flow", () => {
    it("shows authenticating state while auth is loading", () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: null,
        loading: true,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: null,
        loading: true,
        error: null,
      })
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      expect(screen.getByText("Authenticating...")).toBeInTheDocument()
      const spinner = document.querySelector(".animate-spin")
      expect(spinner).toBeInTheDocument()
    })

    it("redirects unauthenticated user to home page", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: null,
        loading: false,
      })

      render(<MapPage />)

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith("/")
      })
    })

    it("fetches ID token when user is authenticated", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: "mock-token-123",
        loading: false,
        error: null,
      })
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      await waitFor(() => {
        expect(useIdToken).toHaveBeenCalledWith(
          expect.objectContaining({
            user: mockUser,
            enabled: true,
          }),
        )
      })
    })

    it("displays error message when token fetch fails", async () => {
      const tokenError = new Error("Failed to get ID token")
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: null,
        loading: false,
        error: tokenError,
      })

      render(<MapPage />)

      await waitFor(() => {
        expect(screen.getByText("Authentication Error")).toBeInTheDocument()
        expect(screen.getByText("Failed to get ID token")).toBeInTheDocument()
      })
    })

    it("allows user to return home when token fetch fails", async () => {
      const tokenError = new Error("Token error")
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: null,
        loading: false,
        error: tokenError,
      })

      const user = userEvent.setup()
      render(<MapPage />)

      const homeButton = screen.getByRole("button", { name: /Return to Home/i })
      await user.click(homeButton)

      expect(mockPush).toHaveBeenCalledWith("/")
    })
  })

  describe("Map Display & Interactions", () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: "mock-token-123",
        loading: false,
        error: null,
      })
    })

    it("renders map with default center coordinates", async () => {
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      await waitFor(() => {
        const mapContainer = screen.getByTestId("map-container")
        expect(mapContainer).toBeInTheDocument()
        const center = JSON.parse(mapContainer.getAttribute("data-center") || "{}")
        expect(center.lat).toBe(37.7704)
        expect(center.lng).toBe(-122.3985)
      })
    })

    it("displays voice recording button", async () => {
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      await waitFor(() => {
        expect(screen.getByTestId("voice-button")).toBeInTheDocument()
        expect(screen.getByRole("button", { name: /Start Recording/i })).toBeInTheDocument()
      })
    })
  })

  describe("Voice Recording & Interaction", () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: "mock-token-123",
        loading: false,
        error: null,
      })
    })

    it("toggles recording state when voice button is clicked", async () => {
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      const user = userEvent.setup()
      const { rerender } = render(<MapPage />)

      const voiceButton = await screen.findByTestId("voice-button")
      await user.click(voiceButton)

      expect(mockStartRecording).toHaveBeenCalled()

      // Simulate recording state
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "recording",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      rerender(<MapPage />)

      expect(await screen.findByRole("button", { name: /Stop Recording/i })).toBeInTheDocument()
    })

    it("displays transcribed text from voice input", async () => {
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "Take me to the nearest gas station",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      await waitFor(() => {
        expect(screen.getByText("Take me to the nearest gas station")).toBeInTheDocument()
      })
    })

    it("processes JSON commands from voice input", async () => {
      const command = {
        action: "set_map_center",
        lat: 40.7128,
        lng: -74.006,
      }
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: JSON.stringify(command),
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      await waitFor(() => {
        const mapContainer = screen.getByTestId("map-container")
        const center = JSON.parse(mapContainer.getAttribute("data-center") || "{}")
        expect(center.lat).toBe(40.7128)
        expect(center.lng).toBe(-74.006)
        expect(screen.getByText("Panning map to new location.")).toBeInTheDocument()
      })
    })

    it("displays agent response as text when command is not JSON", async () => {
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "Here are the nearby restaurants",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      render(<MapPage />)

      await waitFor(() => {
        expect(screen.getByText("Here are the nearby restaurants")).toBeInTheDocument()
      })
    })

    it("clears agent response when new recording starts", async () => {
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "Previous response",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      const user = userEvent.setup()
      const { rerender } = render(<MapPage />)

      expect(screen.getByText("Previous response")).toBeInTheDocument()

      // Simulate recording start
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "recording",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      const voiceButton = screen.getByTestId("voice-button")
      await user.click(voiceButton)

      rerender(<MapPage />)

      await waitFor(() => {
        expect(screen.queryByText("Previous response")).not.toBeInTheDocument()
      })
    })
  })

  describe("Error Handling", () => {
    it("handles malformed JSON in voice input gracefully", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: "mock-token-123",
        loading: false,
        error: null,
      })
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "{invalid json",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation()

      render(<MapPage />)

      await waitFor(
        () => {
          expect(consoleErrorSpy).toHaveBeenCalledWith(
            expect.stringContaining("[v0] Failed to parse command:"),
            expect.any(Error),
          )
        },
        { timeout: 3000 },
      )

      expect(screen.getByText("{invalid json")).toBeInTheDocument()

      consoleErrorSpy.mockRestore()
    })
  })

  describe("Memory Leak Prevention", () => {
    it("cleans up effects on unmount", () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: "mock-token-123",
        loading: false,
        error: null,
      })
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      const { unmount } = render(<MapPage />)

      expect(() => unmount()).not.toThrow()
    })

    it("does not update state after unmount during token fetch", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        loading: false,
      })
      ;(useIdToken as jest.Mock).mockReturnValue({
        idToken: "mock-token-123",
        loading: false,
        error: null,
      })
      ;(useAudio as jest.Mock).mockReturnValue({
        audioState: "idle",
        text: "",
        startRecording: mockStartRecording,
        stopRecording: mockStopRecording,
      })

      const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation()

      const { unmount } = render(<MapPage />)
      unmount()

      await waitFor(() => {
        expect(consoleErrorSpy).not.toHaveBeenCalledWith(
          expect.stringContaining("Can't perform a React state update on an unmounted component"),
        )
      })

      consoleErrorSpy.mockRestore()
    })
  })
})
