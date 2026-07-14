'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Download, Play, Star, Clock, Shield, Loader2, AlertCircle } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

export default function SkillsPage() {
  const [skills, setSkills] = useState<any[]>([]);
  const [categories, setCategories] = useState<{ name: string; label: string; count: number }[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`${apiUrl}/api/v1/skills`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        if (!res.ok) throw new Error('Failed to fetch skills');
        const data = await res.json();
        const skillsList = Array.isArray(data) ? data : data.skills || data.data || [];
        setSkills(skillsList);

        const catMap: Record<string, number> = {};
        skillsList.forEach((s: any) => {
          const cat = s.category || 'other';
          catMap[cat] = (catMap[cat] || 0) + 1;
        });
        const cats = Object.entries(catMap).map(([name, count]) => ({
          name,
          label: name.charAt(0).toUpperCase() + name.slice(1),
          count,
        }));
        setCategories([{ name: 'all', label: 'All Skills', count: skillsList.length }, ...cats]);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    fetchSkills();
  }, []);

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

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
              <AlertCircle className="h-8 w-8 mb-2 text-destructive" />
              <p className="text-destructive font-medium">Failed to load skills</p>
              <p className="text-sm">{error}</p>
            </div>
          ) : (
            <>
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
                          <span>{skill.steps ?? 0} steps</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>{skill.estimatedTime ?? ''}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                          <span>{skill.rating ?? 0}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t">
                        <div className="text-xs text-muted-foreground">
                          {(skill.downloads ?? 0).toLocaleString()} downloads
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
