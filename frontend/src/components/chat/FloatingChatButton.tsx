/**
 * Floating Chat Button Component
 * Modern floating action button for chat access
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { 
  MessageCircle, 
  X, 
  Send, 
  Mic, 
  Minimize2,
  Bot
} from 'lucide-react';

interface FloatingChatButtonProps {
  className?: string;
}

export const FloatingChatButton: React.FC<FloatingChatButtonProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');

  const handleSendMessage = () => {
    if (message.trim()) {
      // TODO: Implement chat functionality
      console.log('Sending message:', message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
      {/* Chat Window */}
      {isOpen && (
        <Card className={`mb-4 shadow-2xl border-0 bg-white/95 backdrop-blur-sm ${
          isMinimized ? 'w-80 h-16' : 'w-96 h-[500px]'
        } transition-all duration-300 ease-in-out`}>
          <CardHeader className={`pb-3 ${isMinimized ? 'py-2' : ''}`}>
            <div className="flex items-center justify-between">
              <CardTitle className={`flex items-center gap-2 ${isMinimized ? 'text-sm' : 'text-lg'}`}>
                <Bot className="w-5 h-5 text-blue-600" />
                <span>Mantra-Mitra</span>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  AI Companion
                </span>
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="h-8 w-8 p-0"
                >
                  <Minimize2 className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8 p-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          
          {!isMinimized && (
            <CardContent className="flex flex-col h-full p-4 pt-0">
              {/* Chat Messages Area */}
              <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-100 rounded-lg p-3 text-sm">
                      <p className="mb-2">• Or just chat about anything</p>
                      <p>You can type or speak to me in any language - I'll understand and respond appropriately. 🌸</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Chat Input */}
              <div className="flex gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Share what's on your mind..."
                  className="flex-1"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  className="px-3"
                >
                  <Mic className="w-4 h-4" />
                </Button>
                <Button
                  onClick={handleSendMessage}
                  size="sm"
                  className="px-3"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          )}
        </Card>
      )}
      
      {/* Floating Action Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-14 h-14 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 ${
          isOpen 
            ? 'bg-red-500 hover:bg-red-600 rotate-45' 
            : 'bg-blue-500 hover:bg-blue-600 hover:scale-110'
        }`}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageCircle className="w-6 h-6 text-white" />
        )}
      </Button>
    </div>
  );
};
