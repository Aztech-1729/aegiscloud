"use client";

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

const faqs = [
  {
    question: 'How does the Windows Agent work?',
    answer: 'The Aegis Cloud Agent is a lightweight Rust application that runs as a Windows service on your PC. It establishes a secure WebSocket connection to our cloud servers and exposes only approved tools for remote management. It uses minimal resources and automatically reconnects if the connection is lost.',
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. All communication uses TLS 1.3 encryption. We use JWT authentication with short-lived tokens, support two-factor authentication, and maintain complete audit logs. The AI assistant can only invoke pre-approved tools — it never executes arbitrary commands on your system.',
  },
  {
    question: 'Can the AI access my files without permission?',
    answer: 'No. The AI operates on a strict allow-list of tools. Every action is visible in your dashboard, and you can monitor what the agent is doing in real-time. You have full control over which tools are enabled for each device.',
  },
  {
    question: 'What Windows versions are supported?',
    answer: 'Aegis Cloud supports Windows 10 (version 1903+) and Windows 11. Both Home and Pro editions are supported. The agent requires a 64-bit operating system and at least 50MB of disk space.',
  },
  {
    question: 'Can I use Aegis Cloud for my business?',
    answer: 'Yes! Our Business and Enterprise plans are designed for teams and organizations. They include role-based access control, API access, audit logs, SSO integration, and dedicated support. Contact us for custom deployment options.',
  },
  {
    question: 'What happens if my PC restarts?',
    answer: 'The agent is installed as a Windows service that starts automatically with your system. After a restart, it will automatically reconnect to Aegis Cloud. No manual intervention needed.',
  },
  {
    question: 'Is there a limit on AI queries?',
    answer: 'The Free plan includes 5 AI queries per day. Pro and Business plans offer unlimited AI queries. Enterprise plans can also set up custom AI models and fine-tune responses for their use case.',
  },
  {
    question: 'Can I self-host Aegis Cloud?',
    answer: 'Enterprise customers can deploy Aegis Cloud on their own infrastructure. This includes on-premise servers, private cloud (AWS, Azure, GCP), or hybrid deployments. Contact our sales team for details.',
  },
];

export function LandingFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section id="faq" className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Frequently Asked{' '}
            <span className="gradient-text">Questions</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Everything you need to know about Aegis Cloud.
          </p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="rounded-xl border border-white/10 bg-card/30 overflow-hidden transition-all duration-200"
            >
              <button
                className="flex items-center justify-between w-full p-5 text-left"
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
              >
                <span className="text-sm font-medium pr-4">{faq.question}</span>
                <ChevronDown
                  className={cn(
                    'h-5 w-5 text-muted-foreground shrink-0 transition-transform duration-200',
                    openIndex === index && 'rotate-180'
                  )}
                />
              </button>
              <div
                className={cn(
                  'overflow-hidden transition-all duration-300',
                  openIndex === index ? 'max-h-96 pb-5' : 'max-h-0'
                )}
              >
                <p className="px-5 text-sm text-muted-foreground leading-relaxed">
                  {faq.answer}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

