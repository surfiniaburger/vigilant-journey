import "@testing-library/jest-dom"
import { render, screen, waitFor } from "@testing-library/react"
import { useRouter } from "next/navigation"
import Page from "@/app/page"
import { useAuth } from "@/context/AuthContext"


jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}))

jest.mock("@/context/AuthContext", () => ({
  useAuth: jest.fn(),
}))

describe("Home Page - Unauthenticated User Journey", () => {
  const mockPush = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  describe("Landing Page Display", () => {
    it("shows landing page content when user is not authenticated", () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: false })

      render(<Page />)

      expect(screen.getByText("Welcome to Alora")).toBeInTheDocument()
      expect(screen.getByText(/Your intelligent automotive co-pilot/i)).toBeInTheDocument()
      expect(screen.getByRole("link", { name: /Launch Co-Pilot/i })).toBeInTheDocument()
    })

    it("displays launch button as the main CTA", () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: false })

      render(<Page />)

      const launchButton = screen.getByRole("link", { name: /Launch Co-Pilot/i })
      expect(launchButton).toBeInTheDocument()
      expect(launchButton).toHaveAttribute("href", "/map")
    })
  })

  describe("Authentication Loading State", () => {
    it("shows loading spinner while authentication is being checked", () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: true })

      render(<Page />)

      const spinner = screen.getByRole("main").querySelector(".animate-spin")
      expect(spinner).toBeInTheDocument()
      expect(spinner).toHaveClass("animate-spin")
    })

    it("does not show landing content during loading", () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: true })

      render(<Page />)

      expect(screen.queryByText("Welcome to Alora")).not.toBeInTheDocument()
    })
  })

  describe("Authenticated User Flow", () => {
    it("redirects to /map when user is authenticated", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: { uid: "test-user", email: "test@example.com" },
        loading: false,
      })

      render(<Page />)

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith("/map")
      })
    })

    it("does not display landing page content when authenticated", () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: { uid: "test-user", email: "test@example.com" },
        loading: false,
      })

      render(<Page />)

      expect(screen.queryByText("Welcome to Alora")).not.toBeInTheDocument()
      expect(screen.queryByRole("link", { name: /Launch Co-Pilot/i })).not.toBeInTheDocument()
    })

    it("handles rapid auth state changes without double redirects", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: true })

      const { rerender } = render(<Page />)
      ;(useAuth as jest.Mock).mockReturnValue({
        user: { uid: "test-user", email: "test@example.com" },
        loading: false,
      })

      rerender(<Page />)

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe("Memory Leak Prevention", () => {
    it("does not throw errors on unmount", () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: false })

      const { unmount } = render(<Page />)

      expect(() => unmount()).not.toThrow()
    })

    it("cleans up effects properly when component unmounts during loading", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: true })

      const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation()

      const { unmount } = render(<Page />)
      unmount()

      await waitFor(() => {
        expect(consoleErrorSpy).not.toHaveBeenCalledWith(
          expect.stringContaining("Can't perform a React state update on an unmounted component"),
        )
      })

      consoleErrorSpy.mockRestore()
    })
  })

  describe("Edge Cases", () => {
    it("handles transition from loading to not authenticated", async () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: true })

      const { rerender } = render(<Page />)

      const spinner = screen.getByRole("main").querySelector(".animate-spin")
      expect(spinner).toBeInTheDocument()
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: false })

      rerender(<Page />)

      await waitFor(() => {
        expect(screen.getByText("Welcome to Alora")).toBeInTheDocument()
      })

      expect(mockPush).not.toHaveBeenCalled()
    })

    it("does not redirect when loading state becomes false with no user", () => {
      ;(useAuth as jest.Mock).mockReturnValue({ user: null, loading: false })

      render(<Page />)

      expect(mockPush).not.toHaveBeenCalled()
    })
  })
})
