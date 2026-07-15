'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { QrCode, Copy, CheckCircle2, Clock, RefreshCw } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

export default function PairDevicePage() {
  const [generatedCode, setGeneratedCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [expiresAt, setExpiresAt] = useState<Date | null>(null);

  const generateCode = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${apiUrl}/api/v1/devices/pair-code`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setGeneratedCode(data.code);
        setExpiresAt(new Date(data.expires_at));
      }
    } catch (error) {
      console.error('Failed to generate code:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(generatedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Pair a New Device</h1>
        <p className="text-muted-foreground">
          Connect your Windows PC to Aegis Cloud in seconds
        </p>
      </div>

      <Card className="border-white/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5 text-aegis-400" />
            Generate Pair Code
          </CardTitle>
          <CardDescription>
            Generate a code to enter in the Windows Agent
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!generatedCode ? (
            <Button
              variant="gradient"
              className="w-full"
              onClick={generateCode}
              disabled={isLoading}
            >
              {isLoading ? 'Generating...' : 'Generate Code'}
            </Button>
          ) : (
            <>
              <div className="relative p-8 rounded-xl bg-gradient-to-br from-aegis-500/10 to-purple-500/10 border border-aegis-500/20">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground mb-2">Pair Code</p>
                  <p className="text-4xl font-mono font-bold tracking-wider text-foreground">
                    {generatedCode}
                  </p>
                  {expiresAt && (
                    <div className="flex items-center justify-center gap-1 mt-3 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>Expires {expiresAt.toLocaleTimeString()}</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1" onClick={copyCode}>
                  {copied ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy Code
                    </>
                  )}
                </Button>
                <Button variant="ghost" onClick={generateCode} disabled={isLoading}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card className="border-white/5 bg-gradient-to-br from-aegis-500/5 to-purple-500/5">
        <CardContent className="p-6">
          <h3 className="font-semibold mb-4">How to pair your device:</h3>
          <ol className="space-y-3 text-sm text-muted-foreground">
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/20 text-aegis-400 flex items-center justify-center text-xs font-bold">
                1
              </span>
              <span>Download and install the Aegis Cloud Agent on your Windows PC</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/20 text-aegis-400 flex items-center justify-center text-xs font-bold">
                2
              </span>
              <span>Click &quot;Generate Code&quot; above to get a pairing code</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/20 text-aegis-400 flex items-center justify-center text-xs font-bold">
                3
              </span>
              <span>Run the agent on your PC and enter the code when prompted</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/20 text-aegis-400 flex items-center justify-center text-xs font-bold">
                4
              </span>
              <span>Once connected, your device will appear on the Devices page</span>
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
