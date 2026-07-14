'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Monitor, Wifi, ListTodo, HardDrive, Activity,
  ArrowUpRight, Cpu, MemoryStick, Plus, Loader2
} from 'lucide-react';
import Link from 'next/link';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

interface Device {
  id?: string;
  name: string;
  status: string;
  cpu?: number;
  ram?: number;
  os?: string;
}

interface ActivityItem {
  action: string;
  device: string;
  time: string;
  status?: string;
}

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const [devicesRes, activityRes, metricsRes] = await Promise.all([
          fetch(`${apiUrl}/api/v1/devices`, { headers: { 'Authorization': `Bearer ${token}` } }).catch(() => null),
          fetch(`${apiUrl}/api/v1/activity?limit=5`, { headers: { 'Authorization': `Bearer ${token}` } }).catch(() => null),
          fetch(`${apiUrl}/api/v1/devices/metrics`, { headers: { 'Authorization': `Bearer ${token}` } }).catch(() => null),
        ]);

        if (devicesRes?.ok) {
          const data = await devicesRes.json();
          setDevices(Array.isArray(data) ? data : (data.devices || data.data || []));
        }

        if (activityRes?.ok) {
          const data = await activityRes.json();
          setRecentActivity(Array.isArray(data) ? data : (data.activity || data.data || []));
        }

        if (metricsRes?.ok) {
          const data = await metricsRes.json();
          const m = Array.isArray(data) ? (data[0] || {}) : (data.metrics || data.data || data);
          setSystemMetrics(m);
        }
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const onlineCount = devices.filter(d => d.status === 'online').length;
  const avgCpu = devices.length ? Math.round(devices.reduce((s, d) => s + (d.cpu || 0), 0) / devices.length) : 0;
  const avgRam = devices.length ? Math.round(devices.reduce((s, d) => s + (d.ram || 0), 0) / devices.length) : 0;

  const stats = [
    { label: 'Total Devices', value: String(devices.length), icon: Monitor, change: `${onlineCount} online`, color: 'text-aegis-400', bg: 'bg-aegis-500/10' },
    { label: 'Online', value: String(onlineCount), icon: Wifi, change: devices.length ? `${Math.round((onlineCount / devices.length) * 100)}% uptime` : '0% uptime', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { label: 'Active Tasks', value: '—', icon: ListTodo, change: 'Sync from API', color: 'text-purple-400', bg: 'bg-purple-500/10' },
    { label: 'Storage Used', value: '—', icon: HardDrive, change: 'N/A', color: 'text-amber-400', bg: 'bg-amber-500/10' },
  ];

  const resourceMetrics = [
    { label: 'CPU Usage', value: systemMetrics.cpu ?? avgCpu, color: 'from-aegis-500 to-blue-500' },
    { label: 'Memory', value: systemMetrics.ram ?? avgRam, color: 'from-purple-500 to-pink-500' },
    { label: 'Disk', value: systemMetrics.disk ?? 0, color: 'from-amber-500 to-orange-500' },
    { label: 'Network', value: systemMetrics.network ?? 0, color: 'from-emerald-500 to-cyan-500' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-aegis-400" />
          <p className="text-sm text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="hover-lift border-white/5">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
              </div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              <p className={`text-xs ${stat.color} mt-2`}>{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 border-white/5">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Devices</CardTitle>
            <Link href="/dashboard/devices">
              <Button variant="ghost" size="sm">View All</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {devices.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No devices found.</p>
            ) : (
              <div className="space-y-3">
                {devices.slice(0, 5).map((device) => (
                  <div
                    key={device.name}
                    className="flex items-center justify-between p-3 rounded-xl bg-secondary/30 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${device.status === 'online' ? 'bg-emerald-400' : 'bg-gray-500'}`} />
                      <div>
                        <p className="text-sm font-medium">{device.name}</p>
                        <p className="text-xs text-muted-foreground">{device.os || 'Unknown OS'}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Cpu className="h-3 w-3" />
                        {device.cpu ?? '—'}%
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <MemoryStick className="h-3 w-3" />
                        {device.ram ?? '—'}%
                      </div>
                      <Badge variant={device.status === 'online' ? 'success' : 'secondary'}>
                        {device.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-white/5">
          <CardHeader>
            <CardTitle className="text-lg">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {recentActivity.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No recent activity.</p>
            ) : (
              <div className="space-y-4">
                {recentActivity.map((activity, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">
                        {activity.device} · {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-white/5">
          <CardHeader>
            <CardTitle className="text-lg">System Resources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {resourceMetrics.map((metric) => (
              <div key={metric.label} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{metric.label}</span>
                  <span className="font-medium">{metric.value}%</span>
                </div>
                <Progress value={metric.value} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/5">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Pair New Device', icon: Plus },
                { label: 'AI Assistant', icon: Activity },
                { label: 'File Manager', icon: HardDrive },
                { label: 'Task History', icon: ListTodo },
              ].map((action) => (
                <button
                  key={action.label}
                  className="flex flex-col items-center gap-2 p-4 rounded-xl border border-white/5 bg-secondary/20 hover:bg-secondary/40 transition-all duration-200 hover-lift"
                >
                  <action.icon className="h-6 w-6 text-aegis-400" />
                  <span className="text-xs text-muted-foreground">{action.label}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
