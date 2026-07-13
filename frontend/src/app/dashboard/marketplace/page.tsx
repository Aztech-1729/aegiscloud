'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Download, Star, Package, Cpu, Wifi, Monitor, HardDrive } from 'lucide-react';

const plugins = [
  {
    id: 'gpu-control',
    name: 'GPU Control',
    description: 'Advanced GPU monitoring and control — overclocking, fan control, performance profiles',
    icon: '🎮',
    category: 'hardware',
    version: '1.0.0',
    author: 'Aegis Cloud',
    tools: 2,
    downloads: 8234,
    rating: 4.7,
    size: '2.4 MB',
    installed: false,
  },
  {
    id: 'docker-manager',
    name: 'Docker Manager',
    description: 'Manage Docker containers, images, and volumes',
    icon: '🐳',
    category: 'developer',
    version: '1.0.0',
    author: 'Aegis Cloud',
    tools: 3,
    downloads: 5621,
    rating: 4.8,
    size: '3.1 MB',
    installed: true,
  },
  {
    id: 'vmware-control',
    name: 'VMware Control',
    description: 'Manage VMware virtual machines',
    icon: '💻',
    category: 'virtualization',
    version: '1.0.0',
    author: 'Aegis Cloud',
    tools: 2,
    downloads: 2341,
    rating: 4.6,
    size: '4.2 MB',
    installed: false,
  },
  {
    id: 'steam-manager',
    name: 'Steam Manager',
    description: 'Manage Steam games and updates',
    icon: '🎯',
    category: 'gaming',
    version: '1.0.0',
    author: 'Community',
    tools: 2,
    downloads: 12456,
    rating: 4.9,
    size: '1.8 MB',
    installed: false,
  },
  {
    id: 'network-monitor',
    name: 'Network Monitor',
    description: 'Advanced network monitoring and diagnostics',
    icon: '🌐',
    category: 'network',
    version: '1.0.0',
    author: 'Aegis Cloud',
    tools: 2,
    downloads: 9876,
    rating: 4.7,
    size: '2.1 MB',
    installed: true,
  },
  {
    id: 'disk-analyzer',
    name: 'Disk Analyzer Pro',
    description: 'Advanced disk space analysis with visualization',
    icon: '📊',
    category: 'maintenance',
    version: '1.0.0',
    author: 'Community',
    tools: 3,
    downloads: 15234,
    rating: 4.8,
    size: '2.8 MB',
    installed: false,
  },
  {
    id: 'process-explorer',
    name: 'Process Explorer',
    description: 'Detailed process monitoring and management',
    icon: '🔍',
    category: 'diagnostic',
    version: '1.0.0',
    author: 'Aegis Cloud',
    tools: 4,
    downloads: 18765,
    rating: 4.9,
    size: '3.5 MB',
    installed: true,
  },
  {
    id: 'registry-cleaner',
    name: 'Registry Cleaner',
    description: 'Safe Windows registry cleaning and optimization',
    icon: '🧹',
    category: 'maintenance',
    version: '1.0.0',
    author: 'Community',
    tools: 2,
    downloads: 22345,
    rating: 4.5,
    size: '1.9 MB',
    installed: false,
  },
];

const categories = [
  { name: 'all', label: 'All Plugins', count: plugins.length },
  { name: 'hardware', label: 'Hardware', count: plugins.filter(p => p.category === 'hardware').length },
  { name: 'developer', label: 'Developer', count: plugins.filter(p => p.category === 'developer').length },
  { name: 'virtualization', label: 'Virtualization', count: plugins.filter(p => p.category === 'virtualization').length },
  { name: 'gaming', label: 'Gaming', count: plugins.filter(p => p.category === 'gaming').length },
  { name: 'network', label: 'Network', count: plugins.filter(p => p.category === 'network').length },
  { name: 'maintenance', label: 'Maintenance', count: plugins.filter(p => p.category === 'maintenance').length },
  { name: 'diagnostic', label: 'Diagnostic', count: plugins.filter(p => p.category === 'diagnostic').length },
];

export default function MarketplacePage() {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredPlugins = plugins.filter(plugin => {
    const matchesSearch = plugin.name.toLowerCase().includes(search.toLowerCase()) ||
                         plugin.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || plugin.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const installedCount = plugins.filter(p => p.installed).length;

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Plugin Marketplace</h1>
        <p className="text-muted-foreground">
          Extend Aegis Cloud with powerful plugins. Add new tools and capabilities.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Plugins</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{plugins.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Available in marketplace</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Installed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-500">{installedCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Active on your devices</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">New Tools</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{plugins.reduce((sum, p) => sum + p.tools, 0)}</div>
            <p className="text-xs text-muted-foreground mt-1">Additional capabilities</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Categories Sidebar */}
        <Card className="w-full md:w-64">
          <CardHeader>
            <CardTitle className="text-lg">Categories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {categories.map(cat => (
              <button
                key={cat.name}
                onClick={() => setSelectedCategory(cat.name)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedCategory === cat.name
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span>{cat.label}</span>
                  <Badge variant="secondary" className="text-xs">{cat.count}</Badge>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Plugins Grid */}
        <div className="flex-1 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search plugins..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPlugins.map(plugin => (
              <Card key={plugin.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="text-4xl">{plugin.icon}</div>
                    {plugin.installed && (
                      <Badge variant="default" className="text-xs">
                        Installed
                      </Badge>
                    )}
                  </div>
                  <CardTitle className="text-lg mt-2">{plugin.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {plugin.description}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Package className="h-3 w-3" />
                      <span>{plugin.tools} tools</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Download className="h-3 w-3" />
                      <span>{plugin.downloads.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                      <span>{plugin.rating}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
                    <span>{plugin.size}</span>
                    <span>by {plugin.author}</span>
                  </div>

                  <div className="flex gap-2 pt-2">
                    {plugin.installed ? (
                      <>
                        <Button size="sm" variant="outline" className="flex-1">
                          Configure
                        </Button>
                        <Button size="sm" variant="ghost">
                          Uninstall
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" variant="default" className="w-full">
                        <Download className="h-3 w-3 mr-1" />
                        Install
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredPlugins.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No plugins found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
