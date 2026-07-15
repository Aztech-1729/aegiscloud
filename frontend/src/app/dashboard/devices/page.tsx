'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Monitor, Cpu, MemoryStick, HardDrive, MoreHorizontal,
  RefreshCw, Power, Trash2, Search, Plus, Filter,
  Activity, Clock, Server, Loader2
} from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

interface Device {
  id: string;
  name: string;
  status: string;
  os: string;
  cpu: string;
  ram: string;
  diskUsed: number;
  diskTotal: number;
  uptime: string;
  agent: string;
  group?: string;
}

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${apiUrl}/api/v1/devices`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (res.ok) {
          const data = await res.json();
          setDevices(Array.isArray(data) ? data : (data.devices || data.data || []));
        }
      } catch (err) {
        console.error('Failed to fetch devices:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDevices();
  }, []);

  const filtered = devices.filter(d =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    (d.group && d.group.toLowerCase().includes(search.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-aegis-400" />
          <p className="text-sm text-muted-foreground">Loading devices...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search devices..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm"><Filter className="h-4 w-4 mr-1" /> Filter</Button>
          <Button variant="gradient" size="sm" onClick={() => window.location.href = '/dashboard/pair-device'}><Plus className="h-4 w-4 mr-1" /> Pair Device</Button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Monitor className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium">No devices found</p>
          <p className="text-sm text-muted-foreground mt-1">Pair a device to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((device) => (
            <Card key={device.id} className="border-white/5 hover:border-white/10 transition-all duration-200 hover-lift group">
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${device.status === 'online' ? 'bg-emerald-500/10' : 'bg-gray-500/10'}`}>
                      <Monitor className={`h-5 w-5 ${device.status === 'online' ? 'text-emerald-400' : 'text-gray-400'}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm">{device.name}</h3>
                      <div className="flex items-center gap-1.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${device.status === 'online' ? 'bg-emerald-400' : 'bg-gray-500'}`} />
                        <span className="text-xs text-muted-foreground capitalize">{device.status}</span>
                      </div>
                    </div>
                  </div>
                  <button className="p-1 rounded hover:bg-accent opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
                  </button>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Server className="h-3 w-3" />
                    <span>{device.os}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Cpu className="h-3 w-3" />
                    <span>{device.cpu}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <MemoryStick className="h-3 w-3" />
                    <span>{device.ram}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <HardDrive className="h-3 w-3" />
                    <span>{device.diskUsed} GB / {device.diskTotal} GB</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>{device.uptime}</span>
                  </div>
                  <Badge variant="outline" className="text-[10px]">{device.agent}</Badge>
                </div>

                <div className="flex items-center gap-2 pt-3 border-t border-white/5">
                  <Button variant="outline" size="sm" className="flex-1 text-xs" disabled={device.status !== 'online'}>
                    <Activity className="h-3 w-3 mr-1" /> Connect
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <RefreshCw className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Power className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive">
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          <Card className="border-dashed border-white/10 hover:border-aegis-500/30 transition-all duration-200 flex items-center justify-center min-h-[280px] cursor-pointer group">
            <div className="text-center">
              <div className="p-3 rounded-full bg-aegis-500/10 mx-auto mb-3 w-fit group-hover:scale-110 transition-transform">
                <Plus className="h-6 w-6 text-aegis-400" />
              </div>
              <p className="text-sm font-medium">Add New Device</p>
              <p className="text-xs text-muted-foreground mt-1">Pair with a code</p>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
