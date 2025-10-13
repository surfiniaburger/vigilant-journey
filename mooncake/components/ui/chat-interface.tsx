'use client';

import { useEffect, useState } from 'react';
import { useAudio } from '@/lib/use-audio';
import { Conversation, ConversationContent, ConversationScrollButton } from '@/components/ui/conversation';
import { Message, MessageContent } from '@/components/ui/message';
import { Response } from '@/components/ui/response';
import { VoiceButton } from './voice-button';

interface ChatMessage {
  id: string;
  from: 'user' | 'assistant';
  text: string;
}

export const ChatInterface = () => {
  const { audioState, text, startRecording, stopRecording } = useAudio();
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    if (text) {
      setMessages(prevMessages => {
        const lastMessage = prevMessages[prevMessages.length - 1];
        if (lastMessage && lastMessage.from === 'assistant') {
          // Update the last message if it's from the assistant
          return [
            ...prevMessages.slice(0, -1),
            { ...lastMessage, text },
          ];
        } else {
          // Add a new message if the last one isn't from the assistant
          return [
            ...prevMessages,
            { id: Date.now().toString(), from: 'assistant', text },
          ];
        }
      });
    }
  }, [text]);

  const handleToggleRecording = () => {
    if (audioState === 'recording') {
      stopRecording();
    } else {
      // When starting a new recording, add a placeholder for the user message
      setMessages(prev => [...prev, { id: Date.now().toString(), from: 'user', text: '' }])
      startRecording();
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      <Conversation className="flex-1">
        <ConversationContent>
          {messages.map(msg => (
            <Message key={msg.id} from={msg.from}>
              <MessageContent>
                {msg.from === 'user' ? (msg.text || 'Listening...') : <Response>{msg.text}</Response>}
              </MessageContent>
            </Message>
          ))}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>
      <div className="p-4 bg-background border-t">
          <VoiceButton
            state={audioState === 'recording' ? 'recording' : 'idle'}
            onPress={handleToggleRecording}
            size="icon"
          />
      </div>
    </div>
  );
};
