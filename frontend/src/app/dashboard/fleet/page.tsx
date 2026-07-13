'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Users, Monitor, Cpu, HardDrive, Activity, MoreVertical } from 'lucide-react';

const mockFleet: any[] = [];

const departments = ['All', 'Engineering', 'Design', 'Sales', 'Operations', 'IT'];

export default function FleetManagementPage() {
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');

  const filteredFleet = mockFleet.filter(device => {
    const matchesSearch = device.name.toLowerCase().includes(search.toLowerCase()) ||
                         device.user.toLowerCase().includes(search.toLowerCase());
    const matchesDept = selectedDept === 'All' || device.department === selectedDept;
    return matchesSearch && matchesDept;
  });

  const onlineCount = mockFleet.filter(d => d.status === 'online').length;
  const offlineCount = mockFleet.filter(d => d.status === 'offline').length;

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Fleet Management</h1>
        <p className="text-muted-foreground">
          Manage all devices across your organization.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Devices</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{mockFleet.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Across {departments.length - 1} departments</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Online</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-500">{onlineCount}</div>
            <p className="text-xs text-muted-foreground mt-1">{Math.round((onlineCount / mockFleet.length) * 100)}% availability</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Offline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-muted-foreground">{offlineCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Last seen varies</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search devices or users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              {departments.map(dept => (
                <Button
                  key={dept}
                  variant={selectedDept === dept ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDept(dept)}
                >
                  {dept}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Devices Table */}
      <Card>
        <CardHeader>
          <CardTitle>Devices ({filteredFleet.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredFleet.map(device => (
              <div
                key={device.id}
                className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className={`w-3 h-3 rounded-full ${
                    device.status === 'online' ? 'bg-green-500' : 'bg-gray-500'
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{device.name}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {device.department}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {device.user}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-sm font-medium">{device.os}</div>
                    <div className="text-xs text-muted-foreground">{device.cpu}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{device.ram}</div>
                    <div className="text-xs text-muted-foreground">RAM</div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {device.policies} policies
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {device.skills} skills
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {device.lastSeen}
                    </div>
                  </div>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {filteredFleet.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              No devices found matching your criteria.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
