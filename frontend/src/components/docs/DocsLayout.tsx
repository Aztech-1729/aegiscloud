import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft, BookOpen, Code2, Shield, Settings, Activity } from 'lucide-react';

export default function DocsLayout({ children, title }: { children: React.ReactNode, title: string }) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border hidden md:flex flex-col fixed h-full top-0 left-0 bg-background/50 backdrop-blur-xl z-10 pt-20">
        <div className="px-6 pb-6">
          <Link href="/">
            <Button variant="ghost" className="w-full justify-start text-muted-foreground mb-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold tracking-tight mb-3 text-foreground">Getting Started</h4>
              <div className="space-y-1">
                <Link href="/docs" className="flex items-center text-sm text-muted-foreground hover:text-aegis-400 py-1">
                  <BookOpen className="mr-2 h-4 w-4" /> Introduction
                </Link>
                <Link href="/docs/api" className="flex items-center text-sm text-muted-foreground hover:text-aegis-400 py-1">
                  <Code2 className="mr-2 h-4 w-4" /> API Reference
                </Link>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold tracking-tight mb-3 text-foreground">Core Features</h4>
              <div className="space-y-1">
                <Link href="/docs" className="flex items-center text-sm text-muted-foreground hover:text-aegis-400 py-1">
                  <Settings className="mr-2 h-4 w-4" /> Agent Installation
                </Link>
                <Link href="/docs" className="flex items-center text-sm text-muted-foreground hover:text-aegis-400 py-1">
                  <Activity className="mr-2 h-4 w-4" /> Task Automation
                </Link>
                <Link href="/docs" className="flex items-center text-sm text-muted-foreground hover:text-aegis-400 py-1">
                  <Shield className="mr-2 h-4 w-4" /> Security Policies
                </Link>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 pt-24 pb-12 px-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">{title}</h1>
          <div className="h-1 w-20 bg-gradient-to-r from-aegis-500 to-aegis-400 rounded-full mt-4"></div>
        </div>
        <div className="prose prose-invert prose-a:text-aegis-400 max-w-none">
          {children}
        </div>
      </main>
    </div>
  );
}
