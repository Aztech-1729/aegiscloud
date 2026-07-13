export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl: string | null;
  plan: PlanType;
  twoFactorEnabled: boolean;
  is_admin: boolean;
  createdAt: string;
  updatedAt: string;
}

export type PlanType = 'free' | 'pro' | 'business' | 'enterprise';

export interface Device {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'connecting';
  windowsVersion: string;
  agentVersion: string;
  cpu: string;
  ram: string;
  gpu: string;
  diskUsage: DiskUsage;
  uptime: number;
  lastSeen: string;
  groupId: string | null;
  stats?: DeviceStats;
}

export interface DeviceStats {
  cpuPercent: number;
  ramPercent: number;
  gpuPercent: number;
  diskPercent: number;
  networkDown: number;
  networkUp: number;
  batteryPercent: number | null;
  temperature: number | null;
}

export interface DiskUsage {
  total: number;
  used: number;
  free: number;
}

export interface DeviceGroup {
  id: string;
  name: string;
  type: 'home' | 'office' | 'gaming' | 'servers' | 'custom';
  deviceCount: number;
  color: string;
}

export interface Task {
  id: string;
  deviceId: string;
  deviceName: string;
  name: string;
  status: TaskStatus;
  progress: number;
  startTime: string;
  endTime: string | null;
  duration: number | null;
  result: TaskResult | null;
  logs: string[];
  createdAt: string;
}

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused';

export interface TaskResult {
  success: boolean;
  message: string;
  data: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  toolCalls?: ToolCall[];
  taskId?: string;
}

export interface ToolCall {
  id: string;
  tool: string;
  params: Record<string, unknown>;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  result?: Record<string, unknown>;
}

export interface FileEntry {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size: number;
  modified: string;
  isDirectory: boolean;
}

export interface Notification {
  id: string;
  type: 'task_completed' | 'device_offline' | 'device_online' | 'update_available' | 'security_alert';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
  actionUrl?: string;
}

export interface Subscription {
  id: string;
  plan: PlanType;
  status: 'active' | 'cancelled' | 'past_due' | 'trialing';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  details: Record<string, unknown>;
  ipAddress: string;
  timestamp: string;
}

export type Theme = 'light' | 'dark' | 'system';
export type Language = 'en' | 'es' | 'fr' | 'de' | 'ja' | 'zh';

export interface Settings {
  theme: Theme;
  language: Language;
  notifications: {
    email: boolean;
    browser: boolean;
    taskCompleted: boolean;
    deviceOffline: boolean;
    updateAvailable: boolean;
  };
  aiModel: string;
  timezone: string;
}
