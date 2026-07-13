'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useThemeStore } from '@/stores';
import {
  Moon, Sun, Monitor, Bell, Globe, Clock, Palette,
  Save, RotateCcw
} from 'lucide-react';

export default function SettingsPage() {
  const { theme, setTheme } = useThemeStore();
  const [notifications, setNotifications] = useState({
    email: true,
    browser: true,
    taskCompleted: true,
    deviceOffline: true,
    updateAvailable: true,
  });

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      <Card className="border-white/5">
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the look and feel of your dashboard</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-3 block">Theme</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: 'light' as const, label: 'Light', icon: Sun },
                  { id: 'dark' as const, label: 'Dark', icon: Moon },
                  { id: 'system' as const, label: 'System', icon: Monitor },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    className={`flex items-center gap-2 p-3 rounded-xl border transition-all ${
                      theme === t.id
                        ? 'border-aegis-500/30 bg-aegis-500/10 text-aegis-400'
                        : 'border-white/10 hover:bg-secondary/30'
                    }`}
                  >
                    <t.icon className="h-4 w-4" />
                    <span className="text-sm">{t.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/5">
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>Choose what notifications you receive</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { key: 'email', label: 'Email Notifications', desc: 'Receive notifications via email' },
            { key: 'browser', label: 'Browser Notifications', desc: 'Show desktop notifications' },
            { key: 'taskCompleted', label: 'Task Completed', desc: 'When a task finishes running' },
            { key: 'deviceOffline', label: 'Device Offline', desc: 'When a device goes offline' },
            { key: 'updateAvailable', label: 'Update Available', desc: 'When agent updates are available' },
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between py-2">
              <div>
                <p className="text-sm font-medium">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
              <button
                onClick={() => setNotifications({ ...notifications, [item.key]: !notifications[item.key as keyof typeof notifications] })}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications[item.key as keyof typeof notifications] ? 'bg-aegis-600' : 'bg-secondary'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications[item.key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card className="border-white/5">
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>General application settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1.5 block flex items-center gap-2">
              <Globe className="h-4 w-4 text-muted-foreground" /> Language
            </label>
            <select className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm">
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
              <option value="ja">日本語</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium mb-1.5 block flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" /> Timezone
            </label>
            <select className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm">
              <option value="Asia/Kolkata">IST (UTC+5:30)</option>
              <option value="America/New_York">EST (UTC-5)</option>
              <option value="Europe/London">GMT (UTC+0)</option>
              <option value="America/Los_Angeles">PST (UTC-8)</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium mb-1.5 block flex items-center gap-2">
              <Palette className="h-4 w-4 text-muted-foreground" /> AI Model
            </label>
            <select className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm">
              <option value="gpt-4">GPT-4 (Recommended)</option>
              <option value="gpt-3.5">GPT-3.5 Turbo</option>
              <option value="claude">Claude 3</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-end gap-3">
        <Button variant="outline"><RotateCcw className="h-4 w-4 mr-1" /> Reset</Button>
        <Button variant="gradient"><Save className="h-4 w-4 mr-1" /> Save Changes</Button>
      </div>
    </div>
  );
}
