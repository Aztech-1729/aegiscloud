'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Building2, Users, Monitor, Shield, Plus, Search,
  MoreHorizontal, ChevronRight, Settings, Key, CreditCard, Loader2, AlertCircle
} from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

const roleColors: Record<string, string> = {
  owner: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  admin: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  manager: 'text-aegis-400 bg-aegis-500/10 border-aegis-500/20',
  technician: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  viewer: 'text-muted-foreground bg-secondary/50 border-border',
};

export default function OrganizationsPage() {
  const [org, setOrg] = useState<any>(null);
  const [departments, setDepartments] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [searchMembers, setSearchMembers] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [orgRes, deptRes, membersRes] = await Promise.all([
          fetch(`${apiUrl}/api/v1/organizations/current`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } }),
          fetch(`${apiUrl}/api/v1/organizations/departments`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } }),
          fetch(`${apiUrl}/api/v1/organizations/members`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } }),
        ]);
        if (!orgRes.ok) throw new Error('Failed to fetch organization');
        const orgData = await orgRes.json();
        setOrg(orgData?.organization || orgData || {});

        if (deptRes.ok) {
          const deptData = await deptRes.json();
          setDepartments(Array.isArray(deptData) ? deptData : deptData.departments || deptData.data || []);
        }
        if (membersRes.ok) {
          const membersData = await membersRes.json();
          setMembers(Array.isArray(membersData) ? membersData : membersData.members || membersData.data || []);
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredMembers = members.filter(m =>
    m.name?.toLowerCase().includes(searchMembers.toLowerCase()) ||
    m.email?.toLowerCase().includes(searchMembers.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Building2 className="h-6 w-6 text-aegis-400" />
            Organization
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage your team, departments, and device access
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm"><Settings className="h-4 w-4 mr-1" /> Settings</Button>
          <Button variant="gradient" size="sm"><Plus className="h-4 w-4 mr-1" /> Invite Member</Button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
          <AlertCircle className="h-8 w-8 mb-2 text-destructive" />
          <p className="text-destructive font-medium">Failed to load organization</p>
          <p className="text-sm">{error}</p>
        </div>
      ) : (
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card className="border-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="h-4 w-4 text-aegis-400" />
              <span className="text-xs text-muted-foreground">Organization</span>
            </div>
            <p className="font-semibold">{org?.name || 'Unnamed'}</p>
            <Badge variant="default" className="text-[10px] mt-1">{org?.plan || 'N/A'}</Badge>
          </CardContent>
        </Card>
        <Card className="border-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Users className="h-4 w-4 text-purple-400" />
              <span className="text-xs text-muted-foreground">Members</span>
            </div>
            <p className="font-semibold">{org?.currentUsers ?? 0} / {org?.maxUsers ?? 0}</p>
            <div className="h-1.5 rounded-full bg-secondary mt-2">
              <div className="h-full rounded-full bg-purple-500" style={{ width: `${org?.maxUsers ? ((org.currentUsers / org.maxUsers) * 100) : 0}%` }} />
            </div>
          </CardContent>
        </Card>
        <Card className="border-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Monitor className="h-4 w-4 text-emerald-400" />
              <span className="text-xs text-muted-foreground">Devices</span>
            </div>
            <p className="font-semibold">{org?.currentDevices ?? 0} / {org?.maxDevices ?? 0}</p>
            <div className="h-1.5 rounded-full bg-secondary mt-2">
              <div className="h-full rounded-full bg-emerald-500" style={{ width: `${org?.maxDevices ? ((org.currentDevices / org.maxDevices) * 100) : 0}%` }} />
            </div>
          </CardContent>
        </Card>
        <Card className="border-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Key className="h-4 w-4 text-amber-400" />
              <span className="text-xs text-muted-foreground">API Keys</span>
            </div>
            <p className="font-semibold">3 Active</p>
            <p className="text-xs text-muted-foreground mt-1">Last used 2h ago</p>
          </CardContent>
        </Card>
      </div>
      )}

      <Tabs defaultValue="members" className="space-y-4">
        <TabsList>
          <TabsTrigger value="members">Members ({loading ? '...' : members.length})</TabsTrigger>
          <TabsTrigger value="departments">Departments ({loading ? '...' : departments.length})</TabsTrigger>
          <TabsTrigger value="devices">Devices</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="members" className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search members..." value={searchMembers} onChange={(e) => setSearchMembers(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" size="sm">Filter</Button>
          </div>

          <Card className="border-white/5">
            <CardContent className="p-0">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : filteredMembers.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  No members found.
                </div>
              ) : (
              <div className="divide-y divide-white/5">
                {filteredMembers.map((member) => (
                  <div key={member.id} className="flex items-center justify-between p-4 hover:bg-secondary/20 transition-colors">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="bg-aegis-500/20 text-aegis-400 text-sm font-medium">
                          {member.name?.split(' ').map((n: string) => n[0]).join('') || '?'}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{member.name}</p>
                        <p className="text-xs text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground">{member.department}</span>
                      <Badge className={`text-[10px] border ${roleColors[member.role] || roleColors.viewer}`}>
                        {member.role}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{member.devices} devices</span>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="departments" className="space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : departments.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No departments found.
            </div>
          ) : (
          departments.map((dept: any) => (
            <Card key={dept.id} className="border-white/5 hover:border-white/10 transition-all cursor-pointer">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-aegis-500/10">
                    <Users className="h-5 w-5 text-aegis-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">{dept.name}</h3>
                    <p className="text-xs text-muted-foreground">{dept.members} members · {dept.devices} devices</p>
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </CardContent>
            </Card>
          ))
          )}
          <Card className="border-dashed border-white/10 hover:border-aegis-500/30 transition-all cursor-pointer">
            <CardContent className="p-4 flex items-center justify-center gap-2 text-muted-foreground">
              <Plus className="h-4 w-4" />
              <span className="text-sm">Add Department</span>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="devices" className="space-y-4">
          <Card className="border-white/5">
            <CardContent className="p-6 text-center">
              <Monitor className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-30" />
              <p className="text-muted-foreground">Organization devices are managed from the main Devices page</p>
              <Button variant="outline" className="mt-4" asChild>
                <a href="/dashboard/devices">View Devices</a>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card className="border-white/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-emerald-400" />
                Security Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { label: 'Require 2FA for all members', description: 'Enforce two-factor authentication', enabled: true },
                { label: 'IP allowlist', description: 'Restrict access to specific IP ranges', enabled: false },
                { label: 'Session timeout', description: 'Auto-logout after inactivity', enabled: true },
                { label: 'Audit logging', description: 'Log all administrative actions', enabled: true },
                { label: 'Command approval', description: 'Require approval for sensitive operations', enabled: false },
              ].map((setting) => (
                <div key={setting.label} className="flex items-center justify-between py-2">
                  <div>
                    <p className="text-sm font-medium">{setting.label}</p>
                    <p className="text-xs text-muted-foreground">{setting.description}</p>
                  </div>
                  <button className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    setting.enabled ? 'bg-aegis-600' : 'bg-secondary'
                  }`}>
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      setting.enabled ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
