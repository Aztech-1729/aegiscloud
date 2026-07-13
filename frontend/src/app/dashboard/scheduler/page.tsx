'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import {
  Calendar, Clock, Plus, Play, Pause, Trash2, Edit2,
  ChevronRight, Zap, HardDrive, RefreshCw, Shield
} from 'lucide-react';

interface Schedule {
  id: string;
  name: string;
  device: string;
  type: 'daily' | 'weekly' | 'monthly' | 'once';
  time: string;
  day?: string;
  commands: Array<{ tool: string; description: string }>;
  active: boolean;
  lastRun: string;
  nextRun: string;
}

const mockSchedules: Schedule[] = [];

const scheduleTypes = [
  { value: 'daily', label: 'Daily', icon: Clock },
  { value: 'weekly', label: 'Weekly', icon: Calendar },
  { value: 'monthly', label: 'Monthly', icon: Calendar },
  { value: 'once', label: 'One-time', icon: Zap },
];

export default function SchedulerPage() {
  const [schedules, setSchedules] = useState(mockSchedules);
  const [showDialog, setShowDialog] = useState(false);

  const toggleSchedule = (id: string) => {
    setSchedules(schedules.map(s =>
      s.id === id ? { ...s, active: !s.active } : s
    ));
  };

  const deleteSchedule = (id: string) => {
    setSchedules(schedules.filter(s => s.id !== id));
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Calendar className="h-6 w-6 text-aegis-400" />
            Task Scheduler
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Schedule maintenance tasks to run automatically
          </p>
        </div>
        <Button variant="gradient" onClick={() => setShowDialog(true)}>
          <Plus className="h-4 w-4 mr-1" /> New Schedule
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-white/5">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-aegis-500/10">
              <Calendar className="h-5 w-5 text-aegis-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{schedules.length}</p>
              <p className="text-xs text-muted-foreground">Total Schedules</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-white/5">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10">
              <Play className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{schedules.filter(s => s.active).length}</p>
              <p className="text-xs text-muted-foreground">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-white/5">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10">
              <Clock className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{schedules.reduce((acc, s) => acc + s.commands.length, 0)}</p>
              <p className="text-xs text-muted-foreground">Scheduled Tasks</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-3">
        {schedules.map((schedule) => (
          <Card key={schedule.id} className="border-white/5 hover:border-white/10 transition-all">
            <CardContent className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <button
                    onClick={() => toggleSchedule(schedule.id)}
                    className={`mt-1 relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      schedule.active ? 'bg-aegis-600' : 'bg-secondary'
                    }`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      schedule.active ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{schedule.name}</h3>
                      <Badge variant={schedule.type === 'daily' ? 'default' : schedule.type === 'weekly' ? 'success' : 'secondary'} className="text-[10px]">
                        {schedule.type}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {schedule.device} · {schedule.time}
                      {schedule.day && ` · ${schedule.day}`}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {schedule.commands.map((cmd, i) => (
                        <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-secondary/50 text-xs text-muted-foreground">
                          {cmd.tool === 'clean_temp' && <HardDrive className="h-3 w-3" />}
                          {cmd.tool === 'cpu_usage' && <Zap className="h-3 w-3" />}
                          {cmd.tool === 'defender_status' && <Shield className="h-3 w-3" />}
                          {cmd.tool === 'run_sfc' && <RefreshCw className="h-3 w-3" />}
                          {cmd.description}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Edit2 className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => deleteSchedule(schedule.id)}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-6 mt-4 pt-3 border-t border-white/5 text-xs text-muted-foreground">
                <span>Last run: {schedule.lastRun}</span>
                <span>Next run: {schedule.nextRun}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Schedule</DialogTitle>
            <DialogDescription>Set up automatic maintenance tasks</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Schedule Name</label>
              <Input placeholder="e.g., Weekly Cleanup" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Device</label>
              <select className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm">
                <option>Work Desktop</option>
                <option>Gaming PC</option>
                <option>Media Server</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-3 block">Frequency</label>
              <div className="grid grid-cols-4 gap-2">
                {scheduleTypes.map((type) => (
                  <button
                    key={type.value}
                    className="flex flex-col items-center gap-1 p-3 rounded-xl border border-white/10 hover:border-aegis-500/30 hover:bg-aegis-500/5 transition-all"
                  >
                    <type.icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs">{type.label}</span>
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Time</label>
              <Input type="time" defaultValue="02:00" />
            </div>
            <div>
              <label className="text-sm font-medium mb-3 block">Tasks to Run</label>
              <div className="space-y-2">
                {['Clean temporary files', 'Empty Recycle Bin', 'Flush DNS', 'Run SFC', 'Check Defender'].map((task) => (
                  <label key={task} className="flex items-center gap-3 p-2 rounded-lg hover:bg-secondary/30 cursor-pointer">
                    <input type="checkbox" className="rounded border-border" />
                    <span className="text-sm">{task}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowDialog(false)}>Cancel</Button>
              <Button variant="gradient" onClick={() => setShowDialog(false)}>Create Schedule</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
