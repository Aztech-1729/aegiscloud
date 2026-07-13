import { Shield, Github, Twitter } from 'lucide-react';
import Link from 'next/link';

const footerLinks = {
  Product: [
    { label: 'Features', href: '#features' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Security', href: '#security' },
    { label: 'Download Agent', href: '/AegisSetup.exe' },
  ],
  Resources: [
    { label: 'Documentation', href: '/docs' },
    { label: 'API Reference', href: '/docs/api' },
  ],
  Legal: [
    { label: 'Privacy Policy', href: '/privacy' },
    { label: 'Terms of Service', href: '/terms' },
  ],
};

export function LandingFooter() {
  return (
    <footer className="border-t border-white/5 pt-16 pb-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Shield className="h-7 w-7 text-aegis-400" />
              <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-aegis-300 to-purple-300">
                Aegis Cloud
              </span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              Securely manage your Windows PCs from anywhere. Powered by AI.
            </p>
            <div className="flex gap-3">
              <a href="#" className="p-2 rounded-lg bg-card/50 border border-white/5 hover:bg-card transition-colors">
                <Github className="h-4 w-4 text-muted-foreground" />
              </a>
              <a href="#" className="p-2 rounded-lg bg-card/50 border border-white/5 hover:bg-card transition-colors">
                <Twitter className="h-4 w-4 text-muted-foreground" />
              </a>
            </div>
          </div>

          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-sm font-semibold mb-4">{title}</h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-white/5 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Aegis Cloud. All rights reserved.
          </p>
          <p className="text-sm text-muted-foreground">
            Built with ❤️ for remote Windows management
          </p>
        </div>
      </div>
    </footer>
  );
}
