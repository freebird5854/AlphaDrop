import React from "react";
import { Link } from "react-router-dom";
import { Zap, ArrowLeft } from "lucide-react";

const Privacy = () => (
  <div className="min-h-screen bg-background text-foreground">
    <div className="noise-overlay" />
    <header className="sticky top-0 z-50 glass-heavy border-b border-border">
      <div className="max-w-4xl mx-auto px-4 lg:px-6 flex items-center h-14 gap-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="p-1.5 bg-primary"><Zap className="w-4 h-4 text-black" /></div>
          <span className="font-heading text-lg font-black uppercase">Alpha<span className="text-primary">Drop</span></span>
        </Link>
        <Link to="/" className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground ml-auto">
          <ArrowLeft className="w-3 h-3" /> Back
        </Link>
      </div>
    </header>

    <main className="max-w-4xl mx-auto px-4 lg:px-6 py-12 prose prose-invert prose-sm" data-testid="privacy-page">
      <h1 className="font-heading text-3xl font-black uppercase tracking-tight text-foreground">Privacy Policy</h1>
      <p className="text-muted-foreground">Last updated: April 2026</p>

      <h2>1. Information We Collect</h2>
      <p>When you use ALPHA DROP, we collect:</p>
      <ul>
        <li><strong>Account Information:</strong> Email address, name, and profile picture (via Google OAuth)</li>
        <li><strong>Payment Information:</strong> Processed securely by Stripe. We never store card numbers.</li>
        <li><strong>Usage Data:</strong> Pages visited, features used, products tracked, and watchlist activity</li>
        <li><strong>Device Information:</strong> Browser type, operating system, device type for optimization</li>
      </ul>

      <h2>2. How We Use Your Information</h2>
      <ul>
        <li>Provide and maintain ALPHA DROP services</li>
        <li>Process subscription payments</li>
        <li>Send product alerts and weekly reports (can be disabled in settings)</li>
        <li>Improve our AlphaScore algorithm and product recommendations</li>
        <li>Communicate about account status and product updates</li>
      </ul>

      <h2>3. Data Sharing</h2>
      <p>We do NOT sell your personal information. We share data only with:</p>
      <ul>
        <li><strong>Stripe:</strong> For payment processing</li>
        <li><strong>Google:</strong> For authentication (OAuth)</li>
        <li><strong>Resend:</strong> For transactional emails</li>
      </ul>

      <h2>4. Data Security</h2>
      <p>We use industry-standard security measures including encrypted connections (HTTPS), secure password hashing (bcrypt), and JWT-based session management. Payment data is handled exclusively by PCI-DSS compliant Stripe.</p>

      <h2>5. Data Retention</h2>
      <p>Account data is retained while your account is active. You may request deletion at any time by contacting support@alphadrop.org. Product tracking data is retained for service improvement.</p>

      <h2>6. Cookies</h2>
      <p>We use essential cookies for authentication (session_token, admin_token). No third-party tracking cookies are used.</p>

      <h2>7. Your Rights</h2>
      <ul>
        <li>Access your personal data</li>
        <li>Request correction of inaccurate data</li>
        <li>Request deletion of your account and data</li>
        <li>Opt out of marketing emails</li>
        <li>Export your data (CSV export feature available)</li>
      </ul>

      <h2>8. Children's Privacy</h2>
      <p>ALPHA DROP is not intended for users under 18. We do not knowingly collect data from minors.</p>

      <h2>9. Changes</h2>
      <p>We may update this policy periodically. Significant changes will be communicated via email.</p>

      <h2>10. Contact</h2>
      <p>For privacy inquiries: <a href="mailto:support@alphadrop.org" className="text-primary">support@alphadrop.org</a></p>
    </main>
  </div>
);

export default Privacy;
