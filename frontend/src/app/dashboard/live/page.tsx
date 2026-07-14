'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Cpu, HardDrive, MemoryStick, Thermometer, Wifi, Zap, Loader2 } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

const MAX_HISTORY = 20;

export default function LiveDashboardPage() {
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(true);
  const historyRef = useRef<Record<string, number[]>>({
    cpu: [], ram: [], gpu: [], disk: [], network: [], temp: [],
  });
  const [, forceUpdate] = useState(0);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/v1/devices/metrics`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (res.ok) {
          const data = await res.json();
          const m: Record<string, number> = Array.isArray(data) ? data[0] : (data.metrics || data.data || data);
          setMetrics(m);

          Object.keys(historyRef.current).forEach(key => {
            if (m[key] !== undefined) {
              historyRef.current[key].push(m[key]);
              if (historyRef.current[key].length > MAX_HISTORY) {
                historyRef.current[key].shift();
              }
            }
          });
          forceUpdate(n => n + 1);
        }
      } catch (err) {
        console.error('Failed to fetch metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const getMetricColor = (value: number) => {
    if (value < 50) return 'text-green-500';
    if (value < 75) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getMetricBg = (value: number) => {
    if (value < 50) return 'bg-green-500/10';
    if (value < 75) return 'bg-yellow-500/10';
    return 'bg-red-500/10';
  };

  const metricDefs = [
    { name: 'CPU', key: 'cpu', icon: Cpu, unit: '%' },
    { name: 'Memory', key: 'ram', icon: MemoryStick, unit: '%' },
    { name: 'GPU', key: 'gpu', icon: Zap, unit: '%' },
    { name: 'Disk', key: 'disk', icon: HardDrive, unit: '%' },
    { name: 'Network', key: 'network', icon: Wifi, unit: 'MB/s' },
    { name: 'Temperature', key: 'temp', icon: Thermometer, unit: '°C' },
  ];

  if (loading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Live Dashboard</h1>
          <p className="text-muted-foreground">Real-time system monitoring with live updates every 5 seconds.</p>
        </div>
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-aegis-400" />
            <p className="text-sm text-muted-foreground">Loading live metrics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Live Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time system monitoring with live updates every 5 seconds.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metricDefs.map(def => {
          const value = metrics?.[def.key] ?? 0;
          const color = getMetricColor(value);
          const bg = getMetricBg(value);
          const sparkline = historyRef.current[def.key] || [];
          return (
            <Card key={def.name} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-lg ${bg}`}>
                    <def.icon className={`h-5 w-5 ${color}`} />
                  </div>
                  <Badge variant="outline" className="text-xs">LIVE</Badge>
                </div>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {def.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end justify-between mb-4">
                  <div>
                    <div className={`text-4xl font-bold ${color}`}>
                      {Math.round(value)}
                    </div>
                    <div className="text-sm text-muted-foreground">{def.unit}</div>
                  </div>
                </div>

                <div className="h-16 flex items-end gap-1">
                  {sparkline.length > 0 ? sparkline.map((v, i) => (
                    <div
                      key={i}
                      className="flex-1 rounded-t transition-all duration-300"
                      style={{
                        height: `${v}%`,
                        backgroundColor: v < 50
                          ? 'rgb(34, 197, 94)'
                          : v < 75
                          ? 'rgb(234, 179, 8)'
                          : 'rgb(239, 68, 68)',
                        opacity: 0.3 + (i / sparkline.length) * 0.7,
                      }}
                    />
                  )) : <div className="flex-1" />}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metrics ? (
              <>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">CPU Usage</div>
                  <div className="font-semibold">{Math.round(metrics.cpu ?? 0)}%</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Memory</div>
                  <div className="font-semibold">{Math.round(metrics.ram ?? 0)}%</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Disk</div>
                  <div className="font-semibold">{Math.round(metrics.disk ?? 0)}%</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Temperature</div>
                  <div className="font-semibold">{Math.round(metrics.temp ?? 0)}°C</div>
                </div>
              </>
            ) : (
              <div className="col-span-4 text-sm text-muted-foreground text-center py-4">
                System information unavailable.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { type: 'info', message: 'Live monitoring active', time: 'Now' },
            ].map((event, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                <Activity className={`h-4 w-4 mt-0.5 ${
                  event.type === 'success' ? 'text-green-500' :
                  event.type === 'warning' ? 'text-yellow-500' :
                  'text-blue-500'
                }`} />
                <div className="flex-1">
                  <div className="text-sm">{event.message}</div>
                  <div className="text-xs text-muted-foreground">{event.time}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
