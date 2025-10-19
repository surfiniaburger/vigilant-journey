'use client';

import { useEffect, useState } from 'react';
import { useAudio } from '@/lib/use-audio';
import { Conversation, ConversationContent, ConversationScrollButton } from '@/components/ui/conversation';
import { Message, MessageContent } from '@/components/ui/message';
import { Response } from '@/components/ui/response';
import { VoiceButton } from './voice-button';
import { Map } from './map';

interface ChatMessage {
  id: string;
  from: 'user' | 'assistant';
  text: string;
}

interface MapCommand {
  action: 'set_map_center';
  lat: number;
  lng: number;
}

export const ChatInterface = ({ idToken }: { idToken: string }) => {
  const { audioState, text, startRecording, stopRecording } = useAudio(idToken);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [mapCenter, setMapCenter] = useState({ lat: 37.7704, lng: -122.3985 });

  const isJsonString = (str: string) => {
    try {
      JSON.parse(str);
    } catch (e) {
      return false;
    }
    return true;
  };

  useEffect(() => {
    if (text) {
      if (isJsonString(text)) {
        try {
          const command: MapCommand = JSON.parse(text);
          if (command.action === 'set_map_center') {
            setMapCenter({ lat: command.lat, lng: command.lng });
            // Optionally add a message to confirm the action
            setMessages(prev => [...prev, { id: Date.now().toString(), from: 'assistant', text: `Roger that! Moving the map.` }]);
            return;
          }
        } catch (e) {}
      }

      setMessages(prevMessages => {
        const lastMessage = prevMessages[prevMessages.length - 1];
        if (lastMessage && lastMessage.from === 'assistant') {
          return [
            ...prevMessages.slice(0, -1),
            { ...lastMessage, text },
          ];
        } else {
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
      setMessages(prev => [...prev, { id: Date.now().toString(), from: 'user', text: '' }])
      startRecording();
    }
  };

  return (
    <div className="w-full h-full flex flex-col md:flex-row">
      <div className="w-full md:w-1/2 h-1/2 md:h-full border-r">
        <Map center={mapCenter} />
      </div>
      <div className="w-full md:w-1/2 h-1/2 md:h-full flex flex-col">
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
        <div className="p-4 bg-background border-t flex justify-center">
            <VoiceButton
              state={audioState === 'recording' ? 'recording' : 'idle'}
              onPress={handleToggleRecording}
              size="icon"
              className="w-16 h-16"
            />
        </div>
      </div>
    </div>
  );
};
