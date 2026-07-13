'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  LayoutDashboard, Monitor, MessageSquare, ListTodo, FolderOpen,
  History, CreditCard, Settings, User, Moon, Sun, Search,
  LogOut, Link2, Shield
} from 'lucide-react';
import { useAuthStore, useThemeStore } from '@/stores';
import { cn } from '@/lib/utils';

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
  keywords?: string[];
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const router = useRouter();
  const { logout } = useAuthStore();
  const { theme, setTheme } = useThemeStore();

  const navigate = (path: string) => {
    router.push(path);
    setIsOpen(false);
    setQuery('');
  };

  const commands: CommandItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, action: () => navigate('/dashboard'), keywords: ['home', 'overview'] },
    { id: 'devices', label: 'Devices', icon: Monitor, action: () => navigate('/dashboard/devices'), keywords: ['pc', 'computer', 'machine'] },
    { id: 'ai', label: 'AI Assistant', icon: MessageSquare, action: () => navigate('/dashboard/ai'), keywords: ['chat', 'help', 'assistant'] },
    { id: 'tasks', label: 'Tasks', icon: ListTodo, action: () => navigate('/dashboard/tasks'), keywords: ['jobs', 'operations'] },
    { id: 'files', label: 'File Manager', icon: FolderOpen, action: () => navigate('/dashboard/files'), keywords: ['browse', 'documents'] },
    { id: 'history', label: 'History', icon: History, action: () => navigate('/dashboard/history'), keywords: ['logs', 'audit'] },
    { id: 'billing', label: 'Billing', icon: CreditCard, action: () => navigate('/dashboard/billing'), keywords: ['payment', 'subscription', 'plan'] },
    { id: 'settings', label: 'Settings', icon: Settings, action: () => navigate('/dashboard/settings'), keywords: ['preferences', 'config'] },
    { id: 'account', label: 'Account', icon: User, action: () => navigate('/dashboard/account'), keywords: ['profile', 'user'] },
    { id: 'pair', label: 'Pair Device', icon: Link2, action: () => navigate('/dashboard/pair-device'), keywords: ['connect', 'add', 'new'] },
    { id: 'theme-dark', label: 'Dark Theme', icon: Moon, action: () => { setTheme('dark'); setIsOpen(false); }, keywords: ['dark mode', 'night'] },
    { id: 'theme-light', label: 'Light Theme', icon: Sun, action: () => { setTheme('light'); setIsOpen(false); }, keywords: ['light mode', 'day'] },
    { id: 'logout', label: 'Sign Out', icon: LogOut, action: () => { logout(); navigate('/'); }, keywords: ['sign out', 'exit', 'leave'] },
  ];

  const filtered = commands.filter((cmd) => {
    const q = query.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(q) ||
      cmd.keywords?.some((k) => k.includes(q)) ||
      cmd.description?.toLowerCase().includes(q)
    );
  });

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      setIsOpen((prev) => !prev);
    }
    if (e.key === 'Escape') {
      setIsOpen(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[20vh]">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsOpen(false)} />
      <div className="relative w-full max-w-lg mx-4 rounded-2xl border border-border bg-card shadow-2xl animate-scale overflow-hidden">
        <div className="flex items-center gap-3 px-4 border-b border-border">
          <Search className="h-4 w-4 text-muted-foreground shrink-0" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or search..."
            className="flex-1 h-12 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-border bg-muted px-1.5 text-[10px] font-medium text-muted-foreground">
            ESC
          </kbd>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 scrollbar-hide">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              No results found for &quot;{query}&quot;
            </div>
          ) : (
            filtered.map((cmd) => (
              <button
                key={cmd.id}
                onClick={() => { cmd.action(); setQuery(''); }}
                className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm hover:bg-accent transition-colors text-left"
              >
                <cmd.icon className="h-4 w-4 text-muted-foreground shrink-0" />
                <span>{cmd.label}</span>
                {cmd.description && (
                  <span className="ml-auto text-xs text-muted-foreground">{cmd.description}</span>
                )}
              </button>
            ))
          )}
        </div>

        <div className="border-t border-border px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><kbd className="px-1 rounded bg-muted border border-border">↑↓</kbd> Navigate</span>
            <span className="flex items-center gap-1"><kbd className="px-1 rounded bg-muted border border-border">↵</kbd> Select</span>
          </div>
          <div className="flex items-center gap-1">
            <Shield className="h-3 w-3 text-aegis-400" />
            <span className="text-xs text-muted-foreground">Aegis Cloud</span>
          </div>
        </div>
      </div>
    </div>
  );
}
