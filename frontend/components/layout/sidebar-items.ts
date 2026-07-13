import {
  LayoutDashboard, Monitor, MessageSquare, ListTodo, FolderOpen,
  History, CreditCard, Settings, User, Shield, LogOut, ChevronLeft,
  Bell, X, Link2, Calendar, Terminal as TerminalIcon, Building2,
  Zap, Package, Activity, Target, ShoppingCart, Sparkles
} from 'lucide-react';

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
