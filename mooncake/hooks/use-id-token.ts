"use client"

import { useEffect, useState } from "react"

interface UseIdTokenOptions {
  user: unknown // Firebase User type - use unknown instead of any for type safety
  enabled?: boolean
}

export function useIdToken({ user, enabled = true }: UseIdTokenOptions) {
  const [idToken, setIdToken] = useState<string | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!enabled || !user) {
      setIdToken(null)
      setLoading(false)
      return
    }

    const controller = new AbortController()
    let isMounted = true

    const getToken = async () => {
      try {
        setLoading(true)
        setError(null)

        const timeoutId = setTimeout(() => {
          controller.abort()
        }, 10000)

        const token = await user.getIdToken()

        clearTimeout(timeoutId)

        if (isMounted && !controller.signal.aborted) {
          setIdToken(token)
        }
      } catch (err) {
        if (isMounted && !controller.signal.aborted) {
          setError(err instanceof Error ? err : new Error("Failed to get ID token"))
          console.error("[v0] Failed to get ID token:", err)
        }
      } finally {
        if (isMounted && !controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    getToken()

    return () => {
      isMounted = false
      controller.abort()
    }
  }, [user, enabled])

  return { idToken, loading, error }
}
