'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Terminal as TerminalIcon, Square, Maximize2, Minimize2,
  Download, Settings, AlertTriangle
} from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

export default function TerminalPage() {
  const [connected, setConnected] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [recording, setRecording] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [commandInput, setCommandInput] = useState('');
  const [history, setHistory] = useState<Array<{ type: 'input' | 'output'; content: string }>>([]);
  const [devices, setDevices] = useState<Array<{ name: string; status: string }>>([]);
  const [devicesLoading, setDevicesLoading] = useState(true);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch(`${apiUrl}/api/v1/devices`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    }).then(res => {
        if (!res.ok) throw new Error('Failed to fetch devices');
        return res.json();
      })
      .then(data => {
        const devs = Array.isArray(data) ? data : data.devices || [];
        setDevices(devs);
        if (devs.length > 0) setSelectedDevice(devs[0].name);
      })
      .catch(() => {})
      .finally(() => setDevicesLoading(false));
  }, []);

  const connect = () => {
    setConnected(true);
    setHistory([
      { type: 'output', content: 'Connected to ' + selectedDevice },
      { type: 'output', content: '' },
      { type: 'output', content: '$' },
    ]);
  };

  const disconnect = () => {
    setConnected(false);
    setHistory([]);
  };

  const executeCommand = async () => {
    if (!commandInput.trim()) return;

    const newHistory = [
      ...history.slice(0, -1),
      { type: 'input' as const, content: commandInput },
    ];

    setHistory([...newHistory, { type: 'output', content: 'Executing...' }]);

    try {
      const res = await fetch(`${apiUrl}/api/v1/terminal/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ device: selectedDevice, command: commandInput }),
      });
      const data = await res.json();
      const output = data.output || data.result || 'Command executed.';
      setHistory([
        ...newHistory,
        { type: 'output', content: output },
        { type: 'output', content: '' },
        { type: 'output', content: '$' },
      ]);
    } catch {
      setHistory([
        ...newHistory,
        { type: 'output', content: 'Error: Failed to execute command.' },
        { type: 'output', content: '' },
        { type: 'output', content: '$' },
      ]);
    }

    setCommandInput('');
  };

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  return (
    <div className={`space-y-4 animate-fade-in ${isFullscreen ? 'fixed inset-0 z-50 bg-background p-4' : ''}`}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <TerminalIcon className="h-6 w-6 text-aegis-400" />
            Remote Terminal
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Secure PTY session with command recording
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
            className="h-9 rounded-lg border border-input bg-background px-3 text-sm"
            disabled={connected}
          >
            {devicesLoading ? (
              <option>Loading...</option>
            ) : (
              devices.map((d) => (
                <option key={d.name} value={d.name} disabled={d.status === 'offline'}>
                  {d.name} ({d.status})
                </option>
              ))
            )}
          </select>
          {!connected ? (
            <Button variant="gradient" size="sm" onClick={connect} disabled={devicesLoading}>
              Connect
            </Button>
          ) : (
            <Button variant="destructive" size="sm" onClick={disconnect}>
              <Square className="h-3.5 w-3.5 mr-1" /> Disconnect
            </Button>
          )}
        </div>
      </div>

      {connected && (
        <div className="flex items-center gap-3 p-3 rounded-xl bg-amber-500/5 border border-amber-500/20">
          <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
          <p className="text-xs text-amber-200">
            This is a secure terminal session. All commands are recorded and auditable.
            Only approved operations can be executed.
          </p>
        </div>
      )}

      <Card className={`border-white/5 ${isFullscreen ? 'flex-1 flex flex-col' : ''}`}>
        <CardHeader className="flex flex-row items-center justify-between py-3 px-4">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-xs text-muted-foreground font-mono">
              {connected ? `${selectedDevice} — cmd.exe` : 'Not connected'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {connected && (
              <>
                <Badge variant={recording ? 'destructive' : 'secondary'} className="text-[10px]">
                  {recording ? '● REC' : 'NOT REC'}
                </Badge>
                <Button
                  variant="ghost" size="icon" className="h-7 w-7"
                  onClick={() => setRecording(!recording)}
                >
                  <div className={`w-2 h-2 rounded-full ${recording ? 'bg-red-500' : 'bg-gray-500'}`} />
                </Button>
                <Button
                  variant="ghost" size="icon" className="h-7 w-7"
                  onClick={() => setIsFullscreen(!isFullscreen)}
                >
                  {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
                </Button>
              </>
            )}
          </div>
        </CardHeader>
        <CardContent className={`p-0 ${isFullscreen ? 'flex-1 flex flex-col' : ''}`}>
          <div
            ref={terminalRef}
            className="bg-[#0c0c0c] font-mono text-sm p-4 overflow-y-auto min-h-[400px] max-h-[500px] text-emerald-400"
            onClick={() => inputRef.current?.focus()}
          >
            {connected ? (
              history.map((entry, i) => (
                <div key={i} className={entry.type === 'input' ? 'text-aegis-300' : 'text-emerald-400/90'}>
                  <pre className="whitespace-pre-wrap">{entry.content}</pre>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <TerminalIcon className="h-12 w-12 mx-auto mb-4 opacity-30" />
                  <p>Connect to a device to start a terminal session</p>
                </div>
              </div>
            )}
          </div>

          {connected && (
            <div className="flex items-center gap-2 p-3 border-t border-white/5 bg-[#0c0c0c]">
              <span className="text-emerald-400 font-mono text-sm">$</span>
              <input
                ref={inputRef}
                type="text"
                value={commandInput}
                onChange={(e) => setCommandInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && executeCommand()}
                className="flex-1 bg-transparent text-emerald-400 font-mono text-sm outline-none caret-emerald-400"
                autoFocus
                spellCheck={false}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
