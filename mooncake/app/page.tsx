import { Button } from "@/components/ui/button";
import { ProtectedLink } from "@/components/ui/ProtectedLink";

export default function Home() {
  return (
    <main className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground">
      <div className="flex flex-col items-center gap-6 text-center">
        <h1 className="text-5xl font-bold tracking-tight md:text-6xl">
          Welcome to Alora
        </h1>
        <p className="max-w-xl text-lg text-muted-foreground">
          Your intelligent automotive co-pilot. Plan trips, diagnose issues, and
          explore your vehicle's features with the power of conversational AI.
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
