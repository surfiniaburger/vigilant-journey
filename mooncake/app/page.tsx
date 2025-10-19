'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Button } from "@/components/ui/button";
import { ProtectedLink } from "@/components/ui/ProtectedLink";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If loading is finished and the user is authenticated, redirect to the map page.
    if (!loading && user) {
      router.push('/map');
    }
  }, [user, loading, router]);

  // While checking auth state, you can show a loader or nothing.
  if (loading || user) {
    return null; // or a loading spinner
  }

  // If not loading and no user, show the landing page.
  return (
    <main className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground">
      <div className="flex flex-col items-center gap-6 text-center">
        <h1 className="text-5xl font-bold tracking-tight md:text-6xl">
          Welcome to Alora
        </h1>
        <p className="max-w-xl text-lg text-muted-foreground">
          Your intelligent automotive co-pilot. Plan trips, diagnose issues, and
          explore your vehicle&apos;s features with the power of conversational AI.
        </p>
        <ProtectedLink href="/map">
          <Button size="lg" className="mt-4">
            Launch Co-Pilot
          </Button>
        </ProtectedLink>
      </div>
    </main>
  );
}
