'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Cpu, HardDrive, MemoryStick, Thermometer, Wifi, Zap } from 'lucide-react';

export default function LiveDashboardPage() {
  const [metrics, setMetrics] = useState({
    cpu: 45,
    ram: 67,
    gpu: 23,
    disk: 54,
    network: 12,
    temp: 62,
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        cpu: Math.max(0, Math.min(100, prev.cpu + (Math.random() - 0.5) * 10)),
        ram: Math.max(0, Math.min(100, prev.ram + (Math.random() - 0.5) * 5)),
        gpu: Math.max(0, Math.min(100, prev.gpu + (Math.random() - 0.5) * 15)),
        disk: Math.max(0, Math.min(100, prev.disk + (Math.random() - 0.5) * 2)),
        network: Math.max(0, Math.min(100, prev.network + (Math.random() - 0.5) * 20)),
        temp: Math.max(30, Math.min(90, prev.temp + (Math.random() - 0.5) * 5)),
      }));
    }, 2000);

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

  const generateSparkline = (baseValue: number, points: number = 20) => {
    const values = [];
    let current = baseValue;
    for (let i = 0; i < points; i++) {
      current = Math.max(0, Math.min(100, current + (Math.random() - 0.5) * 20));
      values.push(current);
    }
    return values;
  };

  const metrics_data = [
    {
      name: 'CPU',
      value: Math.round(metrics.cpu),
      icon: Cpu,
      color: getMetricColor(metrics.cpu),
      bg: getMetricBg(metrics.cpu),
      unit: '%',
      sparkline: generateSparkline(metrics.cpu),
    },
    {
      name: 'Memory',
      value: Math.round(metrics.ram),
      icon: MemoryStick,
      color: getMetricColor(metrics.ram),
      bg: getMetricBg(metrics.ram),
      unit: '%',
      sparkline: generateSparkline(metrics.ram),
    },
    {
      name: 'GPU',
      value: Math.round(metrics.gpu),
      icon: Zap,
      color: getMetricColor(metrics.gpu),
      bg: getMetricBg(metrics.gpu),
      unit: '%',
      sparkline: generateSparkline(metrics.gpu),
    },
    {
      name: 'Disk',
      value: Math.round(metrics.disk),
      icon: HardDrive,
      color: getMetricColor(metrics.disk),
      bg: getMetricBg(metrics.disk),
      unit: '%',
      sparkline: generateSparkline(metrics.disk),
    },
    {
      name: 'Network',
      value: Math.round(metrics.network),
      icon: Wifi,
      color: getMetricColor(metrics.network),
      bg: getMetricBg(metrics.network),
      unit: 'MB/s',
      sparkline: generateSparkline(metrics.network),
    },
    {
      name: 'Temperature',
      value: Math.round(metrics.temp),
      icon: Thermometer,
      color: getMetricColor(metrics.temp),
      bg: getMetricBg(metrics.temp),
      unit: '°C',
      sparkline: generateSparkline(metrics.temp),
    },
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Live Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time system monitoring with live updates every 2 seconds.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics_data.map(metric => (
          <Card key={metric.name} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className={`p-2 rounded-lg ${metric.bg}`}>
                  <metric.icon className={`h-5 w-5 ${metric.color}`} />
                </div>
                <Badge variant="outline" className="text-xs">
                  LIVE
                </Badge>
              </div>
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {metric.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end justify-between mb-4">
                <div>
                  <div className={`text-4xl font-bold ${metric.color}`}>
                    {metric.value}
                  </div>
                  <div className="text-sm text-muted-foreground">{metric.unit}</div>
                </div>
              </div>

              {/* Sparkline Chart */}
              <div className="h-16 flex items-end gap-1">
                {metric.sparkline.map((value, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t transition-all duration-300"
                    style={{
                      height: `${value}%`,
                      backgroundColor: value < 50 
                        ? 'rgb(34, 197, 94)' 
                        : value < 75 
                        ? 'rgb(234, 179, 8)' 
                        : 'rgb(239, 68, 68)',
                      opacity: 0.3 + (i / metric.sparkline.length) * 0.7,
                    }}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* System Info */}
      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-muted-foreground mb-1">OS</div>
              <div className="font-semibold">Windows 11 Pro</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground mb-1">CPU</div>
              <div className="font-semibold">AMD Ryzen 9 5900X</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground mb-1">RAM</div>
              <div className="font-semibold">32 GB DDR4</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground mb-1">GPU</div>
              <div className="font-semibold">NVIDIA RTX 3080</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Events */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { type: 'info', message: 'CPU usage spike to 78%', time: '2 min ago' },
              { type: 'success', message: 'Temp files cleaned (1.2 GB freed)', time: '15 min ago' },
              { type: 'warning', message: 'Memory usage above 80%', time: '1 hour ago' },
              { type: 'info', message: 'DNS cache flushed', time: '2 hours ago' },
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
