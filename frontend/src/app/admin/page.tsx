'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Users, Monitor, CreditCard, Activity, Settings, Shield,
  Search, Filter, Download, MoreHorizontal, TrendingUp,
  Server, Zap, AlertTriangle
} from 'lucide-react';

const mockStats: any[] = [];

const mockUsers: any[] = [];

const mockDevices: any[] = [];

export default function AdminPage() {
  const [searchUsers, setSearchUsers] = useState('');
  const [searchDevices, setSearchDevices] = useState('');

  const filteredUsers = mockUsers.filter(u =>
    u.name.toLowerCase().includes(searchUsers.toLowerCase()) ||
    u.email.toLowerCase().includes(searchUsers.toLowerCase())
  );

  const filteredDevices = mockDevices.filter(d =>
    d.name.toLowerCase().includes(searchDevices.toLowerCase()) ||
    d.user.toLowerCase().includes(searchDevices.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Admin Panel</h1>
        <p className="text-muted-foreground">Manage users, devices, and system-wide settings</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {mockStats.map((stat) => (
          <Card key={stat.label} className="hover-lift border-white/5">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
                <TrendingUp className="h-4 w-4 text-emerald-400" />
              </div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              <p className="text-xs text-emerald-400 mt-2">{stat.change} from last month</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="users" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto">
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="devices">Devices</TabsTrigger>
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          <Card className="border-white/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>Manage all registered users</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search users..."
                      value={searchUsers}
                      onChange={(e) => setSearchUsers(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="outline" size="sm"><Filter className="h-4 w-4 mr-1" /> Filter</Button>
                  <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-1" /> Export</Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/5">
                      <th className="text-left text-xs font-medium text-muted-foreground p-4">User</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-4">Plan</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-4">Status</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-4">Devices</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-4">Joined</th>
                      <th className="text-left text-xs font-medium text-muted-foreground p-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="border-b border-white/5 hover:bg-secondary/20 transition-colors">
                        <td className="p-4">
                          <div>
                            <p className="text-sm font-medium">{user.name}</p>
                            <p className="text-xs text-muted-foreground">{user.email}</p>
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant={user.plan === 'Enterprise' ? 'default' : user.plan === 'Business' ? 'success' : user.plan === 'Pro' ? 'warning' : 'secondary'}>
                            {user.plan}
                          </Badge>
                        </td>
                        <td className="p-4">
                          <Badge variant={user.status === 'active' ? 'success' : 'destructive'}>
                            {user.status}
                          </Badge>
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">{user.devices}</td>
                        <td className="p-4 text-sm text-muted-foreground">{user.created}</td>
                        <td className="p-4">
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="devices" className="space-y-4">
          <Card className="border-white/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Device Management</CardTitle>
                  <CardDescription>View all connected devices</CardDescription>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search devices..."
                    value={searchDevices}
                    onChange={(e) => setSearchDevices(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {filteredDevices.map((device) => (
                  <div key={device.id} className="flex items-center justify-between p-4 rounded-xl bg-secondary/20 hover:bg-secondary/40 transition-colors">
                    <div className="flex items-center gap-3">
                      <Monitor className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">{device.name}</p>
                        <p className="text-xs text-muted-foreground">{device.user} · {device.os}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={device.status === 'online' ? 'success' : 'secondary'}>
                        {device.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{device.lastSeen}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscriptions" className="space-y-4">
          <Card className="border-white/5">
            <CardHeader>
              <CardTitle>Subscription Analytics</CardTitle>
              <CardDescription>Revenue and subscription metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-gradient-to-br from-aegis-500/10 to-purple-500/10 border border-aegis-500/20">
                  <p className="text-sm text-muted-foreground mb-1">Monthly Revenue</p>
                  <p className="text-2xl font-bold">$42,847</p>
                  <p className="text-xs text-emerald-400 mt-1">+18.2% from last month</p>
                </div>
                <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20">
                  <p className="text-sm text-muted-foreground mb-1">Active Subscriptions</p>
                  <p className="text-2xl font-bold">3,421</p>
                  <p className="text-xs text-emerald-400 mt-1">+245 this month</p>
                </div>
                <div className="p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
                  <p className="text-sm text-muted-foreground mb-1">Churn Rate</p>
                  <p className="text-2xl font-bold">2.3%</p>
                  <p className="text-xs text-emerald-400 mt-1">-0.5% from last month</p>
                </div>
              </div>

              <div className="space-y-3">
                {['Free', 'Pro', 'Business', 'Enterprise'].map((plan) => {
                  const counts = { Free: 8426, Pro: 3847, Business: 1421, Enterprise: 127 };
                  return (
                    <div key={plan} className="flex items-center justify-between p-4 rounded-xl bg-secondary/20">
                      <div className="flex items-center gap-3">
                        <CreditCard className="h-5 w-5 text-muted-foreground" />
                        <span className="font-medium">{plan}</span>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">{counts[plan as keyof typeof counts].toLocaleString()}</p>
                        <p className="text-xs text-muted-foreground">users</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="h-5 w-5 text-aegis-400" />
                  System Health
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { label: 'API Server', status: 'healthy', uptime: '99.98%' },
                  { label: 'Database', status: 'healthy', uptime: '99.99%' },
                  { label: 'Redis Cache', status: 'healthy', uptime: '100%' },
                  { label: 'WebSocket', status: 'healthy', uptime: '99.95%' },
                ].map((service) => (
                  <div key={service.label} className="flex items-center justify-between p-3 rounded-lg bg-secondary/20">
                    <span className="text-sm">{service.label}</span>
                    <div className="flex items-center gap-2">
                      <Badge variant="success">{service.status}</Badge>
                      <span className="text-xs text-muted-foreground">{service.uptime}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-amber-400" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Settings className="h-4 w-4 mr-2" />
                  System Settings
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Shield className="h-4 w-4 mr-2" />
                  Security Settings
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Activity className="h-4 w-4 mr-2" />
                  View Audit Logs
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  System Alerts
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
