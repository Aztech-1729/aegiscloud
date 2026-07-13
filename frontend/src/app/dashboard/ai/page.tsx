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

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: Array<{ tool: string; status: 'completed' | 'running' }>;
}

const suggestedActions = [
  { icon: Zap, label: 'My PC is slow', prompt: 'My PC is running slow, can you help?' },
  { icon: Settings, label: 'Restart Explorer', prompt: 'Restart Windows Explorer' },
  { icon: HardDrive, label: 'Clean temp files', prompt: 'Clean temporary files on my PC' },
  { icon: Monitor, label: 'Show processes', prompt: 'Show me the running processes' },
];

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your Aegis Cloud AI assistant. I can help you manage your Windows PC by running approved operations like cleaning files, checking system info, managing processes, and more. What would you like to do?",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDevice] = useState('Work Desktop');
  const messagesEnd = useRef<HTMLDivElement>(null);

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

    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: getAIResponse(input),
        toolCalls: getToolCalls(input),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const getAIResponse = (message: string): string => {
    const lower = message.toLowerCase();
    if (lower.includes('slow')) {
      return "I've analyzed your system. Here's what I found:\n\n• **CPU**: Running at 34% — normal\n• **Memory**: 67% used — some room for improvement\n• **Disk**: 54% used — healthy\n\nI recommend cleaning temporary files and checking startup applications. Would you like me to do that?";
    }
    if (lower.includes('temp') || lower.includes('clean')) {
      return "I've cleaned temporary files. Here's the summary:\n\n• **Files removed**: 1,247\n• **Space freed**: 2.3 GB\n• **Folders cleaned**: Temp, Prefetch, Windows Update Cache\n\nYour system should feel a bit snappier now!";
    }
    if (lower.includes('explorer')) {
      return "Windows Explorer has been restarted successfully. The taskbar and file explorer should refresh momentarily.";
    }
    if (lower.includes('process') || lower.includes('software')) {
      return "Here are the top processes by CPU usage:\n\n1. **Chrome** — 12.3% (8 processes)\n2. **VS Code** — 8.7% (4 processes)\n3. **Discord** — 3.2%\n4. **Windows Defender** — 1.8%\n5. **Explorer** — 0.9%\n\nTotal running processes: 187. Would you like me to show more details?";
    }
    return "I understand your request. Let me check what I can do to help. I'll use the approved tools to assist you safely.";
  };

  const getToolCalls = (message: string) => {
    const lower = message.toLowerCase();
    if (lower.includes('slow')) {
      return [
        { tool: 'cpu_usage', status: 'completed' as const },
        { tool: 'ram_usage', status: 'completed' as const },
        { tool: 'disk_usage', status: 'completed' as const },
      ];
    }
    if (lower.includes('temp') || lower.includes('clean')) {
      return [{ tool: 'clean_temp', status: 'completed' as const }];
    }
    if (lower.includes('explorer')) {
      return [{ tool: 'restart_explorer', status: 'completed' as const }];
    }
    if (lower.includes('process')) {
      return [{ tool: 'list_processes', status: 'completed' as const }];
    }
    return undefined;
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

        {messages.length <= 1 && (
          <div className="px-4 pb-2">
            <p className="text-xs text-muted-foreground mb-2">Suggested actions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedActions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => { setInput(action.prompt); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/5 bg-secondary/20 hover:bg-secondary/40 text-xs text-muted-foreground hover:text-foreground transition-all"
                >
                  <action.icon className="h-3 w-3" />
                  {action.label}
                </button>
              ))}
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
