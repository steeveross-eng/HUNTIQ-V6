/**
 * AIChat - Simple AI chat interface
 * BIONIC Design System compliant - No emojis
 */
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { AIService } from '../AIService';
import { Bot, Send } from 'lucide-react';

export const AIChat = ({ context = {}, onResponse }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Bonjour! Je suis l\'assistant IA Bionic™. Comment puis-je vous aider avec votre chasse?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await AIService.chat(userMessage, context);
      const assistantMessage = response.message || response.response || 'Je n\'ai pas pu traiter votre demande.';
      
      setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }]);
      onResponse?.(response);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Désolé, une erreur est survenue. Veuillez réessayer.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700 h-96 flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Bot className="w-6 h-6 text-purple-400" />
          Assistant IA
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col overflow-hidden p-3">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-3 py-2 ${
                  msg.role === 'user'
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-slate-200'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 rounded-lg px-3 py-2">
                <span className="text-slate-400 text-sm animate-pulse">
                  En train de réfléchir...
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex gap-2 flex-shrink-0">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Posez votre question..."
            className="flex-1 bg-slate-700 border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
            disabled={loading}
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-purple-600 hover:bg-purple-500 px-4"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default AIChat;
