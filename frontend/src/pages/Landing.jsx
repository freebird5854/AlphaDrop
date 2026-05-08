import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Zap,
  TrendingUp,
  Eye,
  Target,
  Lock,
  Play,
  Check,
  ArrowRight,
  Flame,
  Users,
  ShoppingCart,
  BarChart3,
  Bell,
  Bookmark,
} from "lucide-react";

// Mock data for demo
const MOCK_PRODUCTS = [
  {
    id: "demo-1",
    name: "LED Face Therapy Mask",
    category: "Beauty & Skincare",
    price: 45.99,
    alpha_score: 89,
    status: "EXPLOSIVE",
    total_sales: 127500,
    creator_count: 89,
    reason: "Viral velocity detected - 340% growth in 48h",
    image_url: "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400&h=400&fit=crop"
  },
  {
    id: "demo-2", 
    name: "Portable Neck Massager",
    category: "Health & Wellness",
    price: 34.99,
    alpha_score: 82,
    status: "EXPLOSIVE",
    total_sales: 89200,
    creator_count: 67,
    reason: "Creator adoption surging - 127 new creators this week",
    image_url: "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop"
  },
  {
    id: "demo-3",
    name: "Smart Water Bottle",
    category: "Home & Kitchen",
    price: 29.99,
    alpha_score: 76,
    status: "RISING",
    total_sales: 45600,
    creator_count: 43,
    reason: "Steady acceleration - consistent 50%+ weekly growth",
    image_url: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop"
  },
  {
    id: "demo-4",
    name: "Gua Sha Stone Set",
    category: "Beauty & Skincare", 
    price: 18.99,
    alpha_score: 71,
    status: "RISING",
    total_sales: 38900,
    creator_count: 38,
    reason: "Hook patterns matching viral templates",
    image_url: "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400&h=400&fit=crop"
  },
  {
    id: "demo-5",
    name: "Mini Projector HD",
    category: "Tech Gadgets",
    price: 89.99,
    alpha_score: 58,
    status: "EARLY_SIGNAL",
    total_sales: 12400,
    creator_count: 18,
    reason: "Early accumulation detected - 18 creators, 47k avg views",
    image_url: "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&h=400&fit=crop"
  },
];

const Landing = () => {
  const navigate = useNavigate();
  const [showDemo, setShowDemo] = useState(false);

  const getStatusColor = (status) => {
    const colors = {
      EXPLOSIVE: "bg-status-explosive text-black",
      RISING: "bg-status-rising text-black",
      EARLY_SIGNAL: "bg-status-early text-black",
    };
    return colors[status] || "bg-muted";
  };

  const getScoreColor = (score) => {
    if (score >= 72) return "text-status-explosive";
    if (score >= 58) return "text-status-rising";
    return "text-status-early";
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="noise-overlay" />
      
      {/* Header */}
      <header className="sticky top-0 z-50 glass-heavy border-b border-border">
        <div className="max-w-7xl mx-auto px-4 lg:px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary">
                <Zap className="w-5 h-5 text-black" />
              </div>
              <div>
                <h1 className="font-heading text-xl font-black tracking-tighter uppercase leading-none">
                  Alpha<span className="text-primary">Drop</span>
                </h1>
                <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] leading-none">
                  Product Intelligence
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/login")}
                className="font-data text-xs uppercase"
              >
                Login
              </Button>
              <Button
                onClick={() => navigate("/pricing")}
                className="bg-primary text-black font-bold text-xs uppercase"
                data-testid="get-started-btn"
              >
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <Badge className="bg-primary/10 text-primary border-primary/20 mb-6">
            PRODUCT INTELLIGENCE ENGINE
          </Badge>
          <h1 className="font-heading text-5xl md:text-7xl font-black tracking-tighter uppercase leading-none mb-6">
            Find TikTok Shop
            <span className="text-primary block">Winners</span>
            Before They Go Viral
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
            Our Alpha Score algorithm analyzes 7 key factors to identify products 
            in the "accumulation phase" — before they explode.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              onClick={() => navigate("/pricing")}
              size="lg"
              className="btn-skew bg-primary text-black font-bold uppercase tracking-tight px-8"
              data-testid="hero-cta"
            >
              <span className="flex items-center gap-2">
                Start Finding Winners <ArrowRight className="w-5 h-5" />
              </span>
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => setShowDemo(!showDemo)}
              className="font-data uppercase"
              data-testid="see-demo-btn"
            >
              <Play className="w-4 h-4 mr-2" />
              {showDemo ? "Hide Demo" : "See Demo Data"}
            </Button>
          </div>
        </div>
      </section>

      {/* Demo Data Section */}
      {showDemo && (
        <section className="py-12 px-4 border-t border-border">
          <div className="max-w-7xl mx-auto">
            {/* Demo Warning Banner */}
            <div className="glass p-4 mb-8 border-l-4 border-status-rising flex items-center gap-4">
              <Eye className="w-6 h-6 text-status-rising flex-shrink-0" />
              <div>
                <p className="font-bold text-status-rising">DEMO DATA - FOR PREVIEW ONLY</p>
                <p className="text-sm text-muted-foreground">
                  This is sample data to show how ALPHA DROP works. Subscribe to access real TikTok Shop products with live Alpha Scores.
                </p>
              </div>
              <Button
                onClick={() => navigate("/pricing")}
                className="ml-auto bg-status-rising text-black font-bold text-xs uppercase flex-shrink-0"
              >
                Get Real Data
              </Button>
            </div>

            {/* Mock Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: "Products Tracked", value: "250+", icon: ShoppingCart },
                { label: "Explosive", value: "45", icon: Flame, color: "text-status-explosive" },
                { label: "Rising", value: "78", icon: TrendingUp, color: "text-status-rising" },
                { label: "Early Signals", value: "52", icon: Eye, color: "text-status-early" },
              ].map((stat) => (
                <div key={stat.label} className="glass p-4 opacity-75">
                  <div className="flex items-center gap-2 mb-2">
                    <stat.icon className={`w-4 h-4 ${stat.color || "text-muted-foreground"}`} />
                    <span className="text-xs text-muted-foreground uppercase">{stat.label}</span>
                  </div>
                  <p className={`font-data text-2xl font-bold ${stat.color || ""}`}>{stat.value}</p>
                </div>
              ))}
            </div>

            {/* Section Headers */}
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 status-explosive bg-opacity-10 border border-current border-opacity-20">
                <Flame className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-heading text-2xl font-bold tracking-tight uppercase flex items-center gap-3">
                  Explosive Opportunities
                  <Badge variant="outline" className="font-data text-xs">DEMO</Badge>
                </h2>
                <p className="text-sm text-muted-foreground">Products showing viral signals</p>
              </div>
            </div>

            {/* Mock Product Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-12">
              {MOCK_PRODUCTS.map((product) => (
                <div
                  key={product.id}
                  className="group relative bg-card border border-border overflow-hidden opacity-90 hover:opacity-100 transition-opacity"
                >
                  {/* Locked Overlay */}
                  <div className="absolute inset-0 bg-black/60 z-10 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="text-center p-4">
                      <Lock className="w-8 h-8 text-primary mx-auto mb-2" />
                      <p className="text-sm font-medium">Subscribe to Access</p>
                      <p className="text-xs text-muted-foreground">Real product data</p>
                    </div>
                  </div>

                  {/* Image */}
                  <div className="relative aspect-square bg-black/50 overflow-hidden">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover blur-[2px]"
                    />
                    <div className="absolute top-2 right-2 p-2 border bg-status-explosive/10 border-status-explosive/30">
                      <span className={`font-data text-xl font-bold ${getScoreColor(product.alpha_score)}`}>
                        {product.alpha_score}
                      </span>
                    </div>
                    <div className="absolute bottom-2 left-2">
                      <Badge className={`${getStatusColor(product.status)} font-data text-[10px] font-bold uppercase`}>
                        {product.status.replace("_", " ")}
                      </Badge>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-muted-foreground uppercase font-data">
                        {product.category}
                      </span>
                      <TrendingUp className="w-3 h-3 status-explosive" />
                    </div>
                    <div>
                      <h3 className="font-heading text-sm font-bold uppercase tracking-tight line-clamp-1">
                        {product.name}
                      </h3>
                      <p className="font-data text-primary font-medium">
                        ${product.price.toFixed(2)}
                      </p>
                    </div>
                    <div className="flex items-center justify-between text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <ShoppingCart className="w-3 h-3" />
                        <span className="font-data text-xs">{formatNumber(product.total_sales)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        <span className="font-data text-xs">{product.creator_count}</span>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {product.reason}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* CTA */}
            <div className="text-center">
              <Button
                onClick={() => navigate("/pricing")}
                size="lg"
                className="btn-skew bg-primary text-black font-bold uppercase tracking-tight px-12"
              >
                <span className="flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  Unlock Real Data
                </span>
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="py-20 px-4 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-heading text-4xl font-black tracking-tight uppercase mb-4">
              The Alpha Score <span className="text-primary">Algorithm</span>
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our proprietary scoring system analyzes 7 key factors to predict viral potential
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: TrendingUp, title: "Velocity Score", desc: "Sales growth rate over time", pct: "25%" },
              { icon: Users, title: "Creator Adoption", desc: "Unique creators promoting", pct: "20%" },
              { icon: BarChart3, title: "Engagement Quality", desc: "Comments vs likes ratio", pct: "15%" },
              { icon: Target, title: "Hook Strength", desc: "Viral video patterns", pct: "10%" },
            ].map((feature) => (
              <div key={feature.title} className="glass p-6 border-t-2 border-primary">
                <div className="flex items-center justify-between mb-4">
                  <feature.icon className="w-8 h-8 text-primary" />
                  <span className="font-data text-xs text-muted-foreground">{feature.pct} weight</span>
                </div>
                <h3 className="font-heading text-lg font-bold uppercase mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="py-20 px-4 border-t border-border bg-card/50">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="font-heading text-4xl font-black tracking-tight uppercase mb-4">
            Start Finding <span className="text-primary">Winners Today</span>
          </h2>
          <p className="text-muted-foreground mb-12">
            Join thousands of TikTok Shop sellers using ALPHA DROP
          </p>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {[
              { name: "Scout", price: 79, features: ["50 products tracked", "Basic Alpha Score", "7-day history", "CSV export"] },
              { name: "Hunter", price: 199, features: ["500 products", "Full analytics", "Hook intelligence", "Basic affiliate data"], popular: true },
              { name: "Predator", price: 499, features: ["Unlimited products", "API access", "Team seats", "Full affiliate tools"] },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`glass p-6 ${plan.popular ? "border-2 border-primary" : ""}`}
              >
                {plan.popular && (
                  <Badge className="bg-primary text-black font-data text-xs mb-4">MOST POPULAR</Badge>
                )}
                <h3 className="font-heading text-2xl font-bold uppercase mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="font-data text-4xl font-bold">${plan.price}</span>
                  <span className="text-muted-foreground">/mo</span>
                </div>
                <ul className="space-y-2 mb-6 text-left">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-primary" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Button
                  onClick={() => navigate("/pricing")}
                  className={`w-full ${plan.popular ? "bg-primary text-black" : ""}`}
                  variant={plan.popular ? "default" : "outline"}
                >
                  Get Started
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" />
            <span className="font-heading font-bold uppercase">AlphaDrop</span>
          </div>
          <p className="text-sm text-muted-foreground">
            © 2026 ALPHA DROP. Product Intelligence Engine.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
