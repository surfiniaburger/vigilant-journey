import { ChatInterface } from "@/components/ui/chat-interface";

export default function Home() {
  return (
    <main className="flex h-screen items-center justify-center">
      <div className="w-full max-w-lg h-[70vh] border rounded-lg shadow-lg">
        <ChatInterface />
      </div>
    </main>
  );
}
