'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Download, Trash2, Filter, Calendar } from 'lucide-react';

const mockHistory: any[] = [];

export default function HistoryPage() {
  const [search, setSearch] = useState('');
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());

  const filtered = mockHistory.filter(h =>
    h.action.toLowerCase().includes(search.toLowerCase()) ||
    h.device.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search history..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
          </div>
          <Button variant="outline" size="sm"><Filter className="h-4 w-4 mr-1" /> Filter</Button>
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
                {filtered.map((item) => (
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
                      {new Date(item.timestamp).toLocaleString()}
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
