'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Monitor, Wifi, Cpu, MemoryStick, HardDrive, MoreHorizontal,
  RefreshCw, Power, Trash2, Edit2, Search, Plus, Filter,
  Activity, Clock, Server
} from 'lucide-react';

const mockDevices = [
  { id: '1', name: 'Work Desktop', status: 'online', os: 'Windows 11 Pro 23H2', agent: 'v1.2.4', cpu: 'Intel Core i7-13700K', ram: '32 GB DDR5', gpu: 'NVIDIA RTX 4070', diskUsed: 234, diskTotal: 512, uptime: '3d 14h', lastSeen: 'Online now', group: 'Office' },
  { id: '2', name: 'Gaming PC', status: 'online', os: 'Windows 11 Home 23H2', agent: 'v1.2.4', cpu: 'AMD Ryzen 9 7950X', ram: '64 GB DDR5', gpu: 'NVIDIA RTX 4090', diskUsed: 1200, diskTotal: 2000, uptime: '1d 6h', lastSeen: 'Online now', group: 'Gaming' },
  { id: '3', name: 'Home Office', status: 'offline', os: 'Windows 10 Pro 22H2', agent: 'v1.2.3', cpu: 'Intel Core i5-12400', ram: '16 GB DDR4', gpu: 'Intel UHD 730', diskUsed: 89, diskTotal: 256, uptime: '-', lastSeen: '2h ago', group: 'Home' },
  { id: '4', name: 'Media Server', status: 'online', os: 'Windows 11 Pro 23H2', agent: 'v1.2.4', cpu: 'AMD Ryzen 7 7700X', ram: '32 GB DDR5', gpu: 'AMD RX 7800 XT', diskUsed: 3800, diskTotal: 4000, uptime: '14d 2h', lastSeen: 'Online now', group: 'Servers' },
  { id: '5', name: 'Dev Machine', status: 'offline', os: 'Windows 11 Pro 23H2', agent: 'v1.2.4', cpu: 'Intel Core i9-13900K', ram: '128 GB DDR5', gpu: 'NVIDIA RTX 4080', diskUsed: 678, diskTotal: 1000, uptime: '-', lastSeen: '1d ago', group: 'Office' },
  { id: '6', name: 'Backup NAS', status: 'online', os: 'Windows Server 2022', agent: 'v1.2.4', cpu: 'Xeon E-2388G', ram: '64 GB ECC', gpu: 'Matrox D1450', diskUsed: 8500, diskTotal: 16000, uptime: '45d 18h', lastSeen: 'Online now', group: 'Servers' },
];

export default function DevicesPage() {
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const filtered = mockDevices.filter(d =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.group.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search devices..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm"><Filter className="h-4 w-4 mr-1" /> Filter</Button>
          <Button variant="gradient" size="sm"><Plus className="h-4 w-4 mr-1" /> Pair Device</Button>
        </div>
      </div>

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
    </div>
  );
}
