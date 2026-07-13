'use client';

import { cn } from '@/lib/utils';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useSidebarStore, useAuthStore } from '@/stores';
import {
  LayoutDashboard, Monitor, MessageSquare, ListTodo, FolderOpen,
  History, CreditCard, Settings, User, Shield, LogOut, ChevronLeft,
  Bell, X, Link2, Calendar, Terminal as TerminalIcon, Building2,
  Activity, Target, Package, Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useEffect, useState } from 'react';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
  { icon: Monitor, label: 'Devices', href: '/dashboard/devices' },
  { icon: MessageSquare, label: 'AI Assistant', href: '/dashboard/ai' },
  { icon: ListTodo, label: 'Tasks', href: '/dashboard/tasks' },
  { icon: TerminalIcon, label: 'Terminal', href: '/dashboard/terminal' },
  { icon: FolderOpen, label: 'Files', href: '/dashboard/files' },
  { icon: Calendar, label: 'Scheduler', href: '/dashboard/scheduler' },
  { icon: Activity, label: 'Live Dashboard', href: '/dashboard/live' },
  { icon: Target, label: 'Policies', href: '/dashboard/policies' },
  { icon: Sparkles, label: 'Skills', href: '/dashboard/skills' },
  { icon: Package, label: 'Marketplace', href: '/dashboard/marketplace' },
  { icon: Building2, label: 'Fleet', href: '/dashboard/fleet' },
  { icon: History, label: 'History', href: '/dashboard/history' },
  { icon: CreditCard, label: 'Billing', href: '/dashboard/billing' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
  { icon: User, label: 'Account', href: '/dashboard/account' },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { isCollapsed, toggle, setCollapsed } = useSidebarStore();
  const { user, logout } = useAuthStore();
  const [isMobile, setIsMobile] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (!mobile) setMobileOpen(false);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [setCollapsed]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const sidebarContent = (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Shield className="h-7 w-7 text-aegis-400 shrink-0" />
          {(!isCollapsed || isMobile) && (
            <span className="text-lg font-bold gradient-text whitespace-nowrap">Aegis</span>
          )}
        </Link>
        {isMobile ? (
          <button onClick={() => setMobileOpen(false)} className="p-1 rounded-lg hover:bg-accent transition-colors">
            <X className="h-4 w-4" />
          </button>
        ) : (
          <button onClick={toggle} className="p-1 rounded-lg hover:bg-accent transition-colors">
            <ChevronLeft className={cn('h-4 w-4 transition-transform', isCollapsed && 'rotate-180')} />
          </button>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-hide">
        {sidebarItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => isMobile && setMobileOpen(false)}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-aegis-600/10 text-aegis-400 border border-aegis-500/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              )}
            >
              <item.icon className="h-4.5 w-4.5 shrink-0" />
              {(!isCollapsed || isMobile) && <span>{item.label}</span>}
            </Link>
          );
        })}

        {(!isCollapsed || isMobile) && (
          <div className="pt-4 mt-4 border-t border-border">
            <Link
              href="/dashboard/pair-device"
              onClick={() => isMobile && setMobileOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-all"
            >
              <Link2 className="h-4.5 w-4.5 shrink-0" />
              <span>Pair Device</span>
            </Link>
          </div>
        )}
      </nav>

      <div className="p-3 border-t border-border space-y-1">
        {(!isCollapsed || isMobile) && user && (
          <div className="px-3 py-2 mb-2">
            <p className="text-sm font-medium truncate">{user.name}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all w-full"
        >
          <LogOut className="h-4.5 w-4.5 shrink-0" />
          {(!isCollapsed || isMobile) && <span>Sign Out</span>}
        </button>
      </div>
    </div>
  );

  if (isMobile) {
    return (
      <>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
            <aside className="absolute left-0 top-0 h-full w-64 bg-card border-r border-border shadow-2xl animate-fade-in-left">
              {sidebarContent}
            </aside>
          </div>
        )}
      </>
    );
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen border-r border-border bg-card/50 backdrop-blur-xl transition-all duration-300 hidden lg:block',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {sidebarContent}
    </aside>
  );
}

export function DashboardHeader() {
  const { isCollapsed } = useSidebarStore();
  const pathname = usePathname();
  const [isMobile, setIsMobile] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const pageTitle = sidebarItems.find((item) => item.href === pathname)?.label || 'Dashboard';

  return (
    <header
      className={cn(
        'sticky top-0 z-30 h-16 border-b border-border bg-background/80 backdrop-blur-xl transition-all duration-300',
        isMobile ? 'ml-0' : isCollapsed ? 'ml-16' : 'ml-64'
      )}
    >
      <div className="flex items-center justify-between h-full px-4 sm:px-6">
        <div className="flex items-center gap-4">
          {isMobile && (
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="p-2 rounded-lg hover:bg-accent transition-colors"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}
          <h1 className="text-lg sm:text-xl font-semibold">{pageTitle}</h1>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <Link href="/dashboard/pair-device">
            <Button variant="outline" size="sm" className="hidden sm:flex">
              <Link2 className="h-4 w-4 mr-1" />
              Pair Device
            </Button>
          </Link>
          <button className="relative p-2 rounded-lg hover:bg-accent transition-colors">
            <Bell className="h-5 w-5 text-muted-foreground" />
            <Badge className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center text-[10px]">
              3
            </Badge>
          </button>
        </div>
      </div>

      {isMobile && mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-64 bg-card border-r border-border shadow-2xl animate-fade-in-left">
            <div className="flex h-full flex-col">
              <div className="flex items-center justify-between p-4 border-b border-border">
                <Link href="/dashboard" className="flex items-center gap-2" onClick={() => setMobileMenuOpen(false)}>
                  <Shield className="h-7 w-7 text-aegis-400" />
                  <span className="text-lg font-bold gradient-text">Aegis</span>
                </Link>
                <button onClick={() => setMobileMenuOpen(false)} className="p-1 rounded-lg hover:bg-accent">
                  <X className="h-4 w-4" />
                </button>
              </div>
              <nav className="flex-1 overflow-y-auto p-3 space-y-1">
                {sidebarItems.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                        isActive
                          ? 'bg-aegis-600/10 text-aegis-400 border border-aegis-500/20'
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                      )}
                    >
                      <item.icon className="h-4.5 w-4.5 shrink-0" />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </nav>
            </div>
          </aside>
        </div>
      )}
    </header>
  );
}
