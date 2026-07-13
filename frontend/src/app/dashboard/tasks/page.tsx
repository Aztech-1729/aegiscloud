'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import {
  Search, Filter, Clock, CheckCircle2, XCircle, Loader2,
  Play, RotateCcw, Pause, MoreHorizontal
} from 'lucide-react';

const mockTasks = [
  { id: '1', name: 'Clean Temporary Files', device: 'Work Desktop', status: 'completed', progress: 100, startTime: '2024-01-15T10:30:00', duration: '12s', result: 'Cleaned 1,247 files (2.3 GB)' },
  { id: '2', name: 'System Information Scan', device: 'Gaming PC', status: 'running', progress: 65, startTime: '2024-01-15T10:35:00', duration: '...', result: null },
  { id: '3', name: 'Restart Windows Explorer', device: 'Work Desktop', status: 'completed', progress: 100, startTime: '2024-01-15T10:20:00', duration: '3s', result: 'Explorer restarted successfully' },
  { id: '4', name: 'Storage Analysis', device: 'Media Server', status: 'failed', progress: 45, startTime: '2024-01-15T09:45:00', duration: '45s', result: 'Permission denied on C:\\Windows\\System32' },
  { id: '5', name: 'List Installed Applications', device: 'Home Office', status: 'pending', progress: 0, startTime: '2024-01-15T10:40:00', duration: '-', result: null },
  { id: '6', name: 'Flush DNS Cache', device: 'Gaming PC', status: 'completed', progress: 100, startTime: '2024-01-15T09:30:00', duration: '1s', result: 'DNS cache flushed successfully' },
  { id: '7', name: 'Defender Status Check', device: 'Work Desktop', status: 'completed', progress: 100, startTime: '2024-01-15T09:00:00', duration: '5s', result: 'Real-time protection: Active' },
  { id: '8', name: 'Process List', device: 'Dev Machine', status: 'cancelled', progress: 30, startTime: '2024-01-15T08:45:00', duration: '-', result: 'Cancelled by user' },
];

const statusConfig: Record<string, { icon: typeof CheckCircle2; color: string; variant: 'success' | 'warning' | 'destructive' | 'secondary' }> = {
  completed: { icon: CheckCircle2, color: 'text-emerald-400', variant: 'success' },
  running: { icon: Loader2, color: 'text-aegis-400', variant: 'default' },
  failed: { icon: XCircle, color: 'text-red-400', variant: 'destructive' },
  pending: { icon: Clock, color: 'text-amber-400', variant: 'warning' },
  cancelled: { icon: XCircle, color: 'text-gray-400', variant: 'secondary' },
  paused: { icon: Pause, color: 'text-amber-400', variant: 'warning' },
};

export default function TasksPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filtered = mockTasks.filter(task => {
    const matchSearch = task.name.toLowerCase().includes(search.toLowerCase()) || task.device.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || task.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search tasks..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
          </div>
          <div className="flex items-center gap-1 p-1 rounded-lg bg-secondary/30">
            {['all', 'completed', 'running', 'failed', 'pending'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1 rounded-md text-xs font-medium capitalize transition-all ${
                  statusFilter === status ? 'bg-aegis-600 text-white' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {filtered.map((task) => {
          const config = statusConfig[task.status];
          const StatusIcon = config.icon;
          return (
            <Card key={task.id} className="border-white/5 hover:border-white/10 transition-all">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <StatusIcon className={`h-5 w-5 ${config.color} ${task.status === 'running' ? 'animate-spin' : ''}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-medium">{task.name}</h3>
                        <Badge variant={config.variant} className="text-[10px]">{task.status}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {task.device} · {task.duration} · {new Date(task.startTime).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {task.status === 'running' && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Pause className="h-3.5 w-3.5" />
                      </Button>
                    )}
                    {task.status === 'failed' && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <RotateCcw className="h-3.5 w-3.5" />
                      </Button>
                    )}
                    {task.status === 'pending' && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Play className="h-3.5 w-3.5" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreHorizontal className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
                {task.status === 'running' && (
                  <div className="mt-3">
                    <Progress value={task.progress} className="h-1.5" />
                    <p className="text-xs text-muted-foreground mt-1">{task.progress}% complete</p>
                  </div>
                )}
                {task.result && (
                  <p className="text-xs text-muted-foreground mt-2 bg-secondary/30 rounded-lg px-3 py-2">
                    {task.result}
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
