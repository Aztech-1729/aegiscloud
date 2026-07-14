'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Download, Star, Package, Cpu, Wifi, Monitor, HardDrive, Loader2, AlertCircle } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

export default function MarketplacePage() {
  const [plugins, setPlugins] = useState<any[]>([]);
  const [categories, setCategories] = useState<{ name: string; label: string; count: number }[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlugins = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`${apiUrl}/api/v1/plugins`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (!res.ok) throw new Error('Failed to fetch plugins');
        const data = await res.json();
        const pluginsList = Array.isArray(data) ? data : data.plugins || data.data || [];
        setPlugins(pluginsList);

        const catMap: Record<string, number> = {};
        pluginsList.forEach((p: any) => {
          const cat = p.category || 'other';
          catMap[cat] = (catMap[cat] || 0) + 1;
        });
        const cats = Object.entries(catMap).map(([name, count]) => ({
          name,
          label: name.charAt(0).toUpperCase() + name.slice(1),
          count,
        }));
        setCategories([{ name: 'all', label: 'All Plugins', count: pluginsList.length }, ...cats]);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    fetchPlugins();
  }, []);

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
            <div className="text-3xl font-bold">{loading ? '-' : plugins.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Available in marketplace</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Installed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-500">{loading ? '-' : installedCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Active on your devices</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">New Tools</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{loading ? '-' : plugins.reduce((sum, p) => sum + (p.tools?.length ?? 0), 0)}</div>
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

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
              <AlertCircle className="h-8 w-8 mb-2 text-destructive" />
              <p className="text-destructive font-medium">Failed to load plugins</p>
              <p className="text-sm">{error}</p>
            </div>
          ) : (
            <>
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
                          <span>{(plugin.tools?.length ?? 0)} tools</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Download className="h-3 w-3" />
                          <span>{(plugin.downloads ?? 0).toLocaleString()}</span>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
