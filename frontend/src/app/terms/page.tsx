import Link from 'next/link';

export const metadata = {
  title: 'Terms of Service - Aegis Cloud',
  description: 'Read the Aegis Cloud Terms of Service. Understand your rights and responsibilities when using our remote Windows management platform.',
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">Terms of Service</h1>
            <p className="text-xl text-muted-foreground">Last updated: July 14, 2026</p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto prose prose-invert prose-lg">
          <section>
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing or using Aegis Cloud ("the Service"), you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.
            </p>
          </section>

          <section>
            <h2>2. Description of Service</h2>
            <p>
              Aegis Cloud is a remote Windows endpoint management platform that allows users to monitor, control, and automate Windows PCs through a web interface and AI assistant.
            </p>
          </section>

          <section>
            <h2>3. User Accounts</h2>
            <p>
              You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must notify us immediately of any unauthorized use.
            </p>
          </section>

          <section>
            <h2>4. Acceptable Use</h2>
            <p>You agree not to:</p>
            <ul>
              <li>Use the Service for any illegal purpose</li>
              <li>Attempt to gain unauthorized access to other systems</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Reverse engineer or decompile the software</li>
              <li>Share your account credentials</li>
            </ul>
          </section>

          <section>
            <h2>5. Subscription and Payment</h2>
            <p>
              Paid subscriptions are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by law. We reserve the right to change pricing with 30 days notice.
            </p>
          </section>

          <section>
            <h2>6. Data and Privacy</h2>
            <p>
              Your use of the Service is also governed by our Privacy Policy. We collect and process data as described in the Privacy Policy to provide and improve the Service.
            </p>
          </section>

          <section>
            <h2>7. Intellectual Property</h2>
            <p>
              The Service and its original content, features, and functionality are owned by Aegis Cloud and are protected by international copyright, trademark, and other intellectual property laws.
            </p>
          </section>

          <section>
            <h2>8. Termination</h2>
            <p>
              We may terminate or suspend your account immediately, without prior notice, for any reason, including breach of these Terms. Upon termination, your right to use the Service will cease immediately.
            </p>
          </section>

          <section>
            <h2>9. Limitation of Liability</h2>
            <p>
              In no event shall Aegis Cloud be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits, data, or other intangible losses.
            </p>
          </section>

          <section>
            <h2>10. Disclaimer of Warranties</h2>
            <p>
              The Service is provided "as is" without warranties of any kind, either express or implied. We do not warrant that the Service will be uninterrupted, error-free, or completely secure.
            </p>
          </section>

          <section>
            <h2>11. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of India, without regard to its conflict of law provisions.
            </p>
          </section>

          <section>
            <h2>12. Changes to Terms</h2>
            <p>
              We reserve the right to modify these Terms at any time. We will provide notice of significant changes. Your continued use of the Service after such modifications constitutes acceptance of the updated Terms.
            </p>
          </section>

          <section>
            <h2>13. Contact Information</h2>
            <p>
              If you have any questions about these Terms, please contact us at{' '}
              <a href="mailto:legal@aegiscloud.in">legal@aegiscloud.in</a>.
            </p>
          </section>
        </div>
      </main>

      <footer className="border-t border-border bg-card/50 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              © 2026 Aegis Cloud. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link href="/terms" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Terms
              </Link>
              <Link href="/privacy" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Privacy
              </Link>
              <Link href="/contact" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
