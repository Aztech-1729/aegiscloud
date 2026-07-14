'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Send, Bot, User, Loader2, Sparkles, Monitor, Zap,
  HardDrive, Settings, CheckCircle2
} from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: Array<{ tool: string; status: 'completed' | 'running' }>;
}

interface SuggestedAction {
  icon: string;
  label: string;
  prompt: string;
}

const iconMap: Record<string, React.ElementType> = {
  Zap, Settings, HardDrive, Monitor, Sparkles, Bot, Activity: Monitor,
};

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedActions, setSuggestedActions] = useState<SuggestedAction[]>([]);
  const [selectedDevice] = useState('Work Desktop');
  const messagesEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${apiUrl}/api/v1/ai/suggestions`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    }).then(res => res.ok ? res.json() : [])
      .then(data => {
        const list = Array.isArray(data) ? data : (data.suggestions || data.data || []);
        setSuggestedActions(list);
      })
      .catch(() => {});
  }, []);

  const scrollToBottom = () => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${apiUrl}/api/v1/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ message: input, device_id: selectedDevice }),
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.reply || data.message || data.content || 'No response from AI.',
          toolCalls: data.toolCalls || data.tools || undefined,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        setMessages((prev) => [...prev, {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        }]);
      }
    } catch {
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Network error. Please check your connection and try again.',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      <Card className="flex-1 flex flex-col border-white/5 overflow-hidden">
        <div className="p-4 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-aegis-500/10">
              <Sparkles className="h-5 w-5 text-aegis-400" />
            </div>
            <div>
              <h2 className="text-sm font-semibold">AI Assistant</h2>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span className="text-xs text-muted-foreground">Connected to {selectedDevice}</span>
              </div>
            </div>
          </div>
          <Badge variant="success">Online</Badge>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
          {messages.map((message) => (
            <div key={message.id} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.role === 'assistant' && (
                <div className="p-2 rounded-lg bg-aegis-500/10 h-fit">
                  <Bot className="h-4 w-4 text-aegis-400" />
                </div>
              )}
              <div className={`max-w-[70%] ${message.role === 'user' ? 'order-first' : ''}`}>
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-aegis-600 text-white rounded-tr-sm'
                      : 'bg-secondary/50 border border-white/5 rounded-tl-sm'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                </div>
                {message.toolCalls && (
                  <div className="mt-2 space-y-1">
                    {message.toolCalls.map((tc, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                        <span className="font-mono">{tc.tool}</span>
                        <Badge variant="success" className="text-[10px]">{tc.status}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {message.role === 'user' && (
                <div className="p-2 rounded-lg bg-aegis-500/10 h-fit">
                  <User className="h-4 w-4 text-aegis-400" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <div className="p-2 rounded-lg bg-aegis-500/10 h-fit">
                <Bot className="h-4 w-4 text-aegis-400" />
              </div>
              <div className="bg-secondary/50 border border-white/5 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Thinking...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEnd} />
        </div>

        {messages.length === 0 && suggestedActions.length > 0 && (
          <div className="px-4 pb-2">
            <p className="text-xs text-muted-foreground mb-2">Suggested actions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedActions.map((action) => {
                const Icon = iconMap[action.icon] || Monitor;
                return (
                  <button
                    key={action.label}
                    onClick={() => { setInput(action.prompt); }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/5 bg-secondary/20 hover:bg-secondary/40 text-xs text-muted-foreground hover:text-foreground transition-all"
                  >
                    <Icon className="h-3 w-3" />
                    {action.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="p-4 border-t border-white/5">
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="flex items-center gap-3"
          >
            <Input
              placeholder="Ask me to manage your PC..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1"
              disabled={isLoading}
            />
            <Button type="submit" variant="gradient" size="icon" disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
