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

export default function TerminalPage() {
  const [connected, setConnected] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState('Work Desktop');
  const [recording, setRecording] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [commandInput, setCommandInput] = useState('');
  const [history, setHistory] = useState<Array<{ type: 'input' | 'output'; content: string }>>([]);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const devices = [
    { name: 'Work Desktop', status: 'online' },
    { name: 'Gaming PC', status: 'online' },
    { name: 'Media Server', status: 'online' },
    { name: 'Home Office', status: 'offline' },
  ];

  const connect = () => {
    setConnected(true);
    setHistory([
      { type: 'output', content: 'Microsoft Windows [Version 10.0.22631.4460]' },
      { type: 'output', content: '(c) Microsoft Corporation. All rights reserved.' },
      { type: 'output', content: '' },
      { type: 'output', content: 'C:\\Users\\User>' },
    ]);
  };

  const disconnect = () => {
    setConnected(false);
    setHistory([]);
  };

  const executeCommand = () => {
    if (!commandInput.trim()) return;

    const newHistory = [
      ...history.slice(0, -1), // Remove last prompt
      { type: 'input' as const, content: commandInput },
    ];

    // Simulate command output
    const output = getCommandOutput(commandInput);
    newHistory.push({ type: 'output', content: output });
    newHistory.push({ type: 'output', content: '' });
    newHistory.push({ type: 'output', content: 'C:\\Users\\User>' });

    setHistory(newHistory);
    setCommandInput('');
  };

  const getCommandOutput = (cmd: string): string => {
    const lower = cmd.toLowerCase().trim();
    if (lower === 'dir') {
      return ' Volume in drive C has no label.\n Directory of C:\\Users\\User\n\n01/15/2024  10:30 AM    <DIR>          Desktop\n01/15/2024  09:00 AM    <DIR>          Documents\n01/14/2024  03:45 PM    <DIR>          Downloads\n01/13/2024  11:20 AM    <DIR>          Pictures\n               0 File(s)              0 bytes\n               4 Dir(s)  234,567,890,432 bytes free';
    }
    if (lower === 'systeminfo') {
      return 'Host Name:                 WORK-DESKTOP\nOS Name:                   Microsoft Windows 11 Pro\nOS Version:                10.0.22631 N/A Build 22631\nSystem Manufacturer:       Custom\nSystem Model:              Desktop\nProcessor(s):              1 Processor(s) Installed.\n                           [01]: Intel64 Family 6 Model 183 Stepping 1 Genu\nineIntel ~3400 Mhz\nTotal Physical Memory:     32,768 MB\nAvailable Physical Memory: 11,244 MB';
    }
    if (lower.startsWith('ipconfig')) {
      return 'Windows IP Configuration\n\nEthernet adapter Ethernet:\n   Connection-specific DNS Suffix  . : local\n   IPv4 Address. . . . . . . . . . . : 192.168.1.105\n   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n   Default Gateway . . . . . . . . . : 192.168.1.1';
    }
    if (lower === 'help') {
      return 'Available commands: dir, systeminfo, ipconfig, tasklist, cls, help, exit\nNote: This is a secure terminal. All commands are recorded.';
    }
    if (lower === 'tasklist') {
      return 'Image Name                     PID Session Name        Mem Usage\n========================= ======== ================ ============\nSystem Idle Process              0 Services                   8 K\nSystem                           4 Services                 144 K\nchrome.exe                   12840 Console                 345,672 K\nCode.exe                      8234 Console                 234,568 K\nexplorer.exe                  5432 Console                  89,234 K';
    }
    if (lower === 'cls') {
      setHistory([{ type: 'output', content: 'C:\\Users\\User>' }]);
      return '';
    }
    return `'${cmd}' is not recognized as an internal or external command.\nType 'help' for available commands.`;
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
            {devices.map((d) => (
              <option key={d.name} value={d.name} disabled={d.status === 'offline'}>
                {d.name} ({d.status})
              </option>
            ))}
          </select>
          {!connected ? (
            <Button variant="gradient" size="sm" onClick={connect}>
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
              <span className="text-emerald-400 font-mono text-sm">C:\Users\User&gt;</span>
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
