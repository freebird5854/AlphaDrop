import React from "react";
import { Link } from "react-router-dom";
import { Zap, ArrowLeft } from "lucide-react";

const Terms = () => (
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

    <main className="max-w-4xl mx-auto px-4 lg:px-6 py-12 prose prose-invert prose-sm" data-testid="terms-page">
      <h1 className="font-heading text-3xl font-black uppercase tracking-tight text-foreground">Terms of Service</h1>
      <p className="text-muted-foreground">Last updated: April 2026</p>

      <h2>1. Acceptance of Terms</h2>
      <p>By accessing or using ALPHA DROP ("the Service"), you agree to be bound by these Terms. If you do not agree, do not use the Service.</p>

      <h2>2. Service Description</h2>
      <p>ALPHA DROP is a product intelligence platform that provides data analytics, trend predictions, and market insights for TikTok Shop products. The Service includes:</p>
      <ul>
        <li>Product tracking and AlphaScore analytics</li>
        <li>Sales forecasting and market validation</li>
        <li>Creator marketplace and affiliate matching</li>
        <li>Ad creative intelligence</li>
        <li>AI-powered content generation tools</li>
      </ul>

      <h2>3. Account Registration</h2>
      <ul>
        <li>You must provide accurate, current information</li>
        <li>You are responsible for maintaining account security</li>
        <li>You must be at least 18 years old</li>
        <li>One person or entity per account</li>
      </ul>

      <h2>4. Subscription Plans & Payment</h2>
      <ul>
        <li><strong>Scout ($79/mo):</strong> 50 products, basic features</li>
        <li><strong>Hunter ($199/mo):</strong> 500 products, full analytics</li>
        <li><strong>Predator ($499/mo):</strong> Unlimited, API, team seats</li>
        <li>All plans are billed monthly via Stripe</li>
        <li>You may cancel at any time — access continues until end of billing period</li>
        <li>No refunds for partial months</li>
      </ul>

      <h2>5. Proprietary Algorithm</h2>
      <p>The AlphaScore algorithm, scoring methodology, and predictive models are proprietary intellectual property of ALPHA DROP. You may NOT:</p>
      <ul>
        <li>Reverse-engineer the AlphaScore algorithm</li>
        <li>Scrape or bulk-export data for competing services</li>
        <li>Resell or redistribute ALPHA DROP data without written permission</li>
        <li>Use API access (Predator) to build competing products</li>
      </ul>

      <h2>6. Data Accuracy Disclaimer</h2>
      <p>ALPHA DROP provides estimates and predictions based on available data. We do NOT guarantee:</p>
      <ul>
        <li>The accuracy of sales forecasts or revenue estimates</li>
        <li>That products identified as "Explosive" will achieve specific results</li>
        <li>The accuracy of competitor store revenue estimates</li>
        <li>Future product performance based on historical data</li>
      </ul>
      <p><strong>You use this data at your own risk.</strong> ALPHA DROP is a research tool, not financial advice.</p>

      <h2>7. Creator Marketplace</h2>
      <ul>
        <li>ALPHA DROP facilitates connections between sellers and creators</li>
        <li>We are NOT a party to agreements between sellers and creators</li>
        <li>We do NOT guarantee creator performance or payment</li>
        <li>Disputes between parties should be resolved directly</li>
      </ul>

      <h2>8. Acceptable Use</h2>
      <p>You agree NOT to:</p>
      <ul>
        <li>Use automated scraping tools against ALPHA DROP</li>
        <li>Share account credentials</li>
        <li>Interfere with system operation or security</li>
        <li>Use the service for illegal purposes</li>
        <li>Harass creators or other users via the marketplace</li>
      </ul>

      <h2>9. Limitation of Liability</h2>
      <p>ALPHA DROP is provided "as-is" without warranties. In no event shall ALPHA DROP be liable for indirect, incidental, or consequential damages arising from use of the Service. Total liability is limited to fees paid in the preceding 3 months.</p>

      <h2>10. Termination</h2>
      <p>We reserve the right to suspend or terminate accounts that violate these Terms. You may delete your account at any time.</p>

      <h2>11. Changes to Terms</h2>
      <p>We may update these Terms. Continued use after changes constitutes acceptance.</p>

      <h2>12. Governing Law</h2>
      <p>These Terms are governed by the laws of the United States. Disputes shall be resolved through binding arbitration.</p>

      <h2>13. Contact</h2>
      <p>Questions: <a href="mailto:support@alphadrop.org" className="text-primary">support@alphadrop.org</a></p>
    </main>
  </div>
);

export default Terms;
