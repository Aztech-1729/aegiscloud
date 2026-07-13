'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Download, Play, Star, Clock, Shield } from 'lucide-react';

const skills = [
  {
    id: 'gaming-optimization',
    name: 'Gaming Optimization',
    description: 'Optimize your PC for gaming — disable background services, clean caches, optimize settings.',
    icon: '🎮',
    category: 'gaming',
    steps: 6,
    estimatedTime: '2-3 min',
    rating: 4.8,
    downloads: 15847,
    risk: 'low',
  },
  {
    id: 'windows-repair',
    name: 'Windows Repair',
    description: 'Comprehensive Windows repair — fix system files, repair image, flush caches, restart services.',
    icon: '🔧',
    category: 'maintenance',
    steps: 5,
    estimatedTime: '10-15 min',
    rating: 4.9,
    downloads: 23456,
    risk: 'medium',
  },
  {
    id: 'developer-setup',
    name: 'Developer Environment',
    description: 'Check and optimize your development environment — verify tools, check disk, analyze startup.',
    icon: '💻',
    category: 'developer',
    steps: 5,
    estimatedTime: '1-2 min',
    rating: 4.6,
    downloads: 8932,
    risk: 'low',
  },
  {
    id: 'security-audit',
    name: 'Security Audit',
    description: 'Comprehensive security check — verify Defender, Firewall, check for suspicious processes.',
    icon: '🛡️',
    category: 'security',
    steps: 6,
    estimatedTime: '3-5 min',
    rating: 4.9,
    downloads: 31222,
    risk: 'low',
  },
  {
    id: 'deep-cleanup',
    name: 'Deep Cleanup',
    description: 'Thorough system cleanup — temp files, recycle bin, DNS cache, storage analysis.',
    icon: '🧹',
    category: 'maintenance',
    steps: 5,
    estimatedTime: '3-5 min',
    rating: 4.7,
    downloads: 45678,
    risk: 'low',
  },
  {
    id: 'network-diagnostic',
    name: 'Network Diagnostic',
    description: 'Full network diagnostic — check adapters, DNS, IP, connectivity.',
    icon: '🌐',
    category: 'network',
    steps: 3,
    estimatedTime: '1 min',
    rating: 4.5,
    downloads: 12345,
    risk: 'low',
  },
  {
    id: 'startup-optimizer',
    name: 'Startup Optimizer',
    description: 'Analyze and optimize startup programs to speed up boot time.',
    icon: '⚡',
    category: 'optimization',
    steps: 4,
    estimatedTime: '1-2 min',
    rating: 4.6,
    downloads: 19876,
    risk: 'low',
  },
  {
    id: 'full-system-check',
    name: 'Full System Check',
    description: 'Complete system health check — all metrics, security, storage, and performance.',
    icon: '🔍',
    category: 'diagnostic',
    steps: 9,
    estimatedTime: '3-5 min',
    rating: 4.9,
    downloads: 56789,
    risk: 'low',
  },
];

const categories = [
  { name: 'all', label: 'All Skills', count: skills.length },
  { name: 'gaming', label: 'Gaming', count: skills.filter(s => s.category === 'gaming').length },
  { name: 'maintenance', label: 'Maintenance', count: skills.filter(s => s.category === 'maintenance').length },
  { name: 'developer', label: 'Developer', count: skills.filter(s => s.category === 'developer').length },
  { name: 'security', label: 'Security', count: skills.filter(s => s.category === 'security').length },
  { name: 'network', label: 'Network', count: skills.filter(s => s.category === 'network').length },
  { name: 'optimization', label: 'Optimization', count: skills.filter(s => s.category === 'optimization').length },
  { name: 'diagnostic', label: 'Diagnostic', count: skills.filter(s => s.category === 'diagnostic').length },
];

export default function SkillsPage() {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredSkills = skills.filter(skill => {
    const matchesSearch = skill.name.toLowerCase().includes(search.toLowerCase()) ||
                         skill.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || skill.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Skills Marketplace</h1>
        <p className="text-muted-foreground">
          One command, multiple tools. Install skills to automate complex tasks.
        </p>
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

        {/* Skills Grid */}
        <div className="flex-1 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search skills..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSkills.map(skill => (
              <Card key={skill.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="text-4xl">{skill.icon}</div>
                    <Badge variant={skill.risk === 'low' ? 'secondary' : skill.risk === 'medium' ? 'warning' : 'destructive'}>
                      {skill.risk} risk
                    </Badge>
                  </div>
                  <CardTitle className="text-lg mt-2">{skill.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {skill.description}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Play className="h-3 w-3" />
                      <span>{skill.steps} steps</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{skill.estimatedTime}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                      <span>{skill.rating}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t">
                    <div className="text-xs text-muted-foreground">
                      {skill.downloads.toLocaleString()} downloads
                    </div>
                    <Button size="sm" variant="default">
                      <Play className="h-3 w-3 mr-1" />
                      Run
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredSkills.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No skills found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
