'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores';
import { cn } from '@/lib/utils';
import { Shield, LayoutDashboard, Users, CreditCard, Activity, Monitor, Settings, LogOut, ChevronLeft } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useSidebarStore } from '@/stores';

const adminItems = [
  { icon: LayoutDashboard, label: 'Overview', href: '/admin' },
  { icon: Users, label: 'Users', href: '/admin' },
  { icon: Monitor, label: 'Devices', href: '/admin' },
  { icon: CreditCard, label: 'Subscriptions', href: '/admin' },
  { icon: Activity, label: 'System', href: '/admin' },
  { icon: Settings, label: 'Settings', href: '/admin' },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const { isCollapsed, toggle } = useSidebarStore();

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user?.is_admin)) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, user, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="h-8 w-8 rounded-full border-2 border-aegis-400 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-background">
      <aside
        className={cn(
          'fixed left-0 top-0 z-40 h-screen border-r border-border bg-card/50 backdrop-blur-xl transition-all duration-300',
          isCollapsed ? 'w-16' : 'w-64'
        )}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <Link href="/admin" className="flex items-center gap-2">
              <Shield className="h-7 w-7 text-destructive shrink-0" />
              {!isCollapsed && (
                <span className="text-lg font-bold text-destructive">Admin</span>
              )}
            </Link>
            <button onClick={toggle} className="p-1 rounded-lg hover:bg-accent transition-colors">
              <ChevronLeft className={cn('h-4 w-4 transition-transform', isCollapsed && 'rotate-180')} />
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-hide">
            {adminItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                  'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                )}
              >
                <item.icon className="h-4.5 w-4.5 shrink-0" />
                {!isCollapsed && <span>{item.label}</span>}
              </Link>
            ))}
          </nav>

          <div className="p-3 border-t border-border">
            <Link
              href="/dashboard"
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-all"
            >
              <LayoutDashboard className="h-4.5 w-4.5 shrink-0" />
              {!isCollapsed && <span>Back to Dashboard</span>}
            </Link>
          </div>
        </div>
      </aside>

      <header
        className={cn(
          'sticky top-0 z-30 h-16 border-b border-border bg-background/80 backdrop-blur-xl transition-all duration-300',
          isCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <div className="flex items-center justify-between h-full px-6">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded-md bg-destructive/10 text-destructive text-xs font-medium">
              Admin
            </span>
          </div>
        </div>
      </header>

      <main className={cn('transition-all duration-300 p-6', isCollapsed ? 'ml-16' : 'ml-64')}>
        {children}
      </main>
    </div>
  );
}
