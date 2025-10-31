"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { ProtectedLink } from "@/components/ui/ProtectedLink"

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted || loading) return

    if (user) {
      router.push("/map")
    }
  }, [user, loading, router, mounted])

  if (!mounted || loading) {
    return (
      <main className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-muted border-t-foreground" />
      </main>
    )
  }

  // Only show landing if user is not authenticated
  if (user) {
    return null
  }

  return (
    <main className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground">
      <div className="flex flex-col items-center gap-6 text-center">
        <h1 className="text-5xl font-bold tracking-tight md:text-6xl">Welcome to Alora</h1>
        <p className="max-w-xl text-lg text-muted-foreground">
          Your intelligent automotive co-pilot. Plan trips, diagnose issues, and explore your vehicle&apos;s features
          with the power of conversational AI.
        </p>
        <ProtectedLink href="/map">
          <Button size="lg" className="mt-4">
            Launch Co-Pilot
          </Button>
        </ProtectedLink>
      </div>
    </main>
  )
}
