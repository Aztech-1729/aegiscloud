'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Download, Trash2, Filter, Calendar, Loader2 } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

export default function HistoryPage() {
  const [search, setSearch] = useState('');
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const fetchHistory = () => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    const qs = params.toString();
    fetch(`${apiUrl}/api/v1/history${qs ? `?${qs}` : ''}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    }).then(res => {
        if (!res.ok) throw new Error('Failed to fetch history');
        return res.json();
      })
      .then(data => setHistory(Array.isArray(data) ? data : data.history || []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search history..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="h-9 rounded-lg border border-input bg-background px-3 text-sm"
            />
            <span className="text-xs text-muted-foreground">to</span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="h-9 rounded-lg border border-input bg-background px-3 text-sm"
            />
            <Button variant="outline" size="sm" onClick={fetchHistory}>
              <Filter className="h-4 w-4 mr-1" /> Filter
            </Button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-1" /> Export</Button>
          {selectedItems.size > 0 && (
            <Button variant="destructive" size="sm"><Trash2 className="h-4 w-4 mr-1" /> Delete Selected</Button>
          )}
        </div>
      </div>

      <Card className="border-white/5">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left text-xs font-medium text-muted-foreground p-4 w-10">
                    <input type="checkbox" className="rounded border-border" />
                  </th>
                  <th className="text-left text-xs font-medium text-muted-foreground p-4">Action</th>
                  <th className="text-left text-xs font-medium text-muted-foreground p-4">Device</th>
                  <th className="text-left text-xs font-medium text-muted-foreground p-4">Status</th>
                  <th className="text-left text-xs font-medium text-muted-foreground p-4">Duration</th>
                  <th className="text-left text-xs font-medium text-muted-foreground p-4">Triggered By</th>
                  <th className="text-left text-xs font-medium text-muted-foreground p-4">Time</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={7} className="text-center py-12">
                      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground mx-auto" />
                    </td>
                  </tr>
                )}
                {error && (
                  <tr>
                    <td colSpan={7} className="text-center py-12">
                      <p className="text-sm text-red-400">{error}</p>
                    </td>
                  </tr>
                )}
                {!loading && !error && history.length === 0 && (
                  <tr>
                    <td colSpan={7} className="text-center py-12">
                      <p className="text-sm text-muted-foreground">No history found</p>
                    </td>
                  </tr>
                )}
                {!loading && !error && history.map((item) => (
                  <tr key={item.id} className="border-b border-white/5 hover:bg-secondary/20 transition-colors">
                    <td className="p-4">
                      <input
                        type="checkbox"
                        className="rounded border-border"
                        checked={selectedItems.has(item.id)}
                        onChange={(e) => {
                          const next = new Set(selectedItems);
                          if (e.target.checked) next.add(item.id);
                          else next.delete(item.id);
                          setSelectedItems(next);
                        }}
                      />
                    </td>
                    <td className="p-4 text-sm font-medium">{item.action}</td>
                    <td className="p-4 text-sm text-muted-foreground">{item.device}</td>
                    <td className="p-4">
                      <Badge variant={item.status === 'success' ? 'success' : item.status === 'failed' ? 'destructive' : 'secondary'}>
                        {item.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-sm text-muted-foreground">{item.duration}</td>
                    <td className="p-4">
                      <Badge variant="outline">{item.user}</Badge>
                    </td>
                    <td className="p-4 text-sm text-muted-foreground">
                      {item.timestamp ? new Date(item.timestamp).toLocaleString() : ''}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
