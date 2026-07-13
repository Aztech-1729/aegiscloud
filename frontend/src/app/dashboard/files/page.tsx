'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Folder, FileText, Image, Video, Music, Archive, Code,
  Search, Upload, Download, Trash2, Edit2, ChevronRight,
  Home, ArrowLeft, MoreHorizontal
} from 'lucide-react';

const mockFiles = [
  { name: 'Documents', type: 'folder', size: '-', modified: '2024-01-15', items: 42 },
  { name: 'Downloads', type: 'folder', size: '-', modified: '2024-01-15', items: 128 },
  { name: 'Pictures', type: 'folder', size: '-', modified: '2024-01-14', items: 256 },
  { name: 'Videos', type: 'folder', size: '-', modified: '2024-01-10', items: 15 },
  { name: 'Desktop', type: 'folder', size: '-', modified: '2024-01-15', items: 23 },
  { name: 'report-final.docx', type: 'file', size: '2.4 MB', modified: '2024-01-15' },
  { name: 'budget-2024.xlsx', type: 'file', size: '856 KB', modified: '2024-01-14' },
  { name: 'presentation.pptx', type: 'file', size: '15.2 MB', modified: '2024-01-13' },
  { name: 'screenshot.png', type: 'file', size: '1.1 MB', modified: '2024-01-12' },
  { name: 'backup.zip', type: 'file', size: '450 MB', modified: '2024-01-10' },
  { name: 'notes.txt', type: 'file', size: '4 KB', modified: '2024-01-15' },
  { name: 'config.json', type: 'file', size: '2 KB', modified: '2024-01-08' },
];

function getFileIcon(name: string, type: string) {
  if (type === 'folder') return <Folder className="h-5 w-5 text-amber-400" />;
  if (name.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i)) return <Image className="h-5 w-5 text-emerald-400" />;
  if (name.match(/\.(mp4|avi|mov|mkv)$/i)) return <Video className="h-5 w-5 text-purple-400" />;
  if (name.match(/\.(mp3|wav|flac|ogg)$/i)) return <Music className="h-5 w-5 text-pink-400" />;
  if (name.match(/\.(zip|rar|7z|tar|gz)$/i)) return <Archive className="h-5 w-5 text-orange-400" />;
  if (name.match(/\.(js|ts|py|rs|json|xml|html|css)$/i)) return <Code className="h-5 w-5 text-cyan-400" />;
  return <FileText className="h-5 w-5 text-aegis-400" />;
}

export default function FilesPage() {
  const [search, setSearch] = useState('');
  const [currentPath, setCurrentPath] = useState(['C:', 'Users', 'User']);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const filtered = mockFiles.filter(f =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <Card className="border-white/5">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" className="h-8 w-8" disabled={currentPath.length <= 1}>
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div className="flex items-center gap-1 text-sm">
                <Home className="h-4 w-4 text-muted-foreground" />
                {currentPath.map((segment, i) => (
                  <span key={i} className="flex items-center gap-1">
                    <ChevronRight className="h-3 w-3 text-muted-foreground" />
                    <span className={i === currentPath.length - 1 ? 'font-medium' : 'text-muted-foreground'}>
                      {segment}
                    </span>
                  </span>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative max-w-xs">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search files..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10 h-8 text-sm" />
              </div>
              <Button variant="outline" size="sm"><Upload className="h-4 w-4 mr-1" /> Upload</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1">
            <div className="flex items-center gap-3 px-3 py-2 text-xs text-muted-foreground border-b border-white/5">
              <span className="flex-1">Name</span>
              <span className="w-24 text-right">Size</span>
              <span className="w-32 text-right">Modified</span>
              <span className="w-10" />
            </div>
            {filtered.map((file) => (
              <div
                key={file.name}
                onClick={() => setSelectedFile(file.name)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                  selectedFile === file.name ? 'bg-aegis-600/10 border border-aegis-500/20' : 'hover:bg-secondary/30'
                }`}
              >
                {getFileIcon(file.name, file.type)}
                <span className="flex-1 text-sm font-medium truncate">{file.name}</span>
                <span className="w-24 text-right text-xs text-muted-foreground">{file.size}</span>
                <span className="w-32 text-right text-xs text-muted-foreground">{file.modified}</span>
                <div className="w-10 flex items-center justify-end gap-1">
                  {file.type === 'file' && (
                    <Button variant="ghost" size="icon" className="h-7 w-7">
                      <Download className="h-3.5 w-3.5" />
                    </Button>
                  )}
                  <Button variant="ghost" size="icon" className="h-7 w-7">
                    <MoreHorizontal className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
