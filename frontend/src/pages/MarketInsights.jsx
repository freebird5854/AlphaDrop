import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import { Badge } from "../components/ui/badge";
import { Skeleton } from "../components/ui/skeleton";
import {
  Globe,
  Zap,
  ShoppingBag,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  Target,
  Layers,
} from "lucide-react";

const MarketInsights = () => {
  const navigate = useNavigate();
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await api.getMarketValidation();
      setData(res.data);
    } catch (e) {
      console.error("Failed to load market validation:", e);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (val) => {
    if (val >= 75) return "text-status-explosive";
    if (val >= 50) return "text-status-rising";
    if (val >= 25) return "text-status-early";
    return "text-status-avoid";
  };

  const scoreBg = (val) => {
    if (val >= 75) return "bg-status-explosive";
    if (val >= 50) return "bg-status-rising";
    if (val >= 25) return "bg-status-early";
    return "bg-status-avoid";
  };

  const formatNum = (n) => {
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
    return String(n);
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6" data-testid="market-insights-loading">
          <Skeleton className="h-32 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-48" />)}
          </div>
        </div>
      </Layout>
    );
  }

  if (!data) {
    return (
      <Layout>
        <div className="text-center py-20">
          <p className="text-muted-foreground">Failed to load market validation data.</p>
        </div>
      </Layout>
    );
  }

  const platforms = [
    { key: "tiktok_demand", label: "TikTok Shop", icon: Zap, color: "text-primary" },
    { key: "amazon_demand", label: "Amazon", icon: ShoppingBag, color: "text-status-rising" },
    { key: "google_trends", label: "Google Trends", icon: TrendingUp, color: "text-status-early" },
  ];

  return (
    <Layout>
      <div className="space-y-8" data-testid="market-insights-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-accent/10 border border-accent/30">
              <Globe className="w-7 h-7 text-accent" />
            </div>
            <div>
              <h1 className="font-heading text-3xl md:text-4xl font-black tracking-tighter uppercase leading-none">
                Market <span className="text-accent">Validation</span>
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Cross-platform demand analysis across {data.total_products_analyzed} products
              </p>
            </div>
          </div>
          {beginnerMode && (
            <div className="glass p-3 max-w-sm border-l-2 border-accent">
              <p className="text-xs text-muted-foreground">
                <span className="text-accent font-bold">TIP:</span> Products with high demand on
                TikTok but low on Amazon represent arbitrage opportunities — sell where demand
                exceeds supply.
              </p>
            </div>
          )}
        </div>

        {/* Platform Averages */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {platforms.map((platform) => {
            const avg = data.platform_averages[platform.key];
            return (
              <div key={platform.key} className="glass p-5" data-testid={`platform-avg-${platform.key}`}>
                <div className="flex items-center gap-2 mb-3">
                  <platform.icon className={`w-5 h-5 ${platform.color}`} />
                  <span className="text-sm font-data uppercase tracking-wider">{platform.label}</span>
                </div>
                <div className="flex items-end gap-2 mb-3">
                  <span className={`font-data text-4xl font-bold ${scoreColor(avg)}`}>{avg}</span>
                  <span className="text-xs text-muted-foreground mb-1">/ 100 avg</span>
                </div>
                <div className="h-2 bg-card border border-border overflow-hidden">
                  <div
                    className={`h-full ${scoreBg(avg)} transition-all duration-700`}
                    style={{ width: `${avg}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Category Breakdown */}
        <div className="glass p-6" data-testid="category-breakdown">
          <div className="flex items-center gap-3 mb-6">
            <Layers className="w-5 h-5 text-primary" />
            <h2 className="font-heading text-xl font-bold uppercase tracking-tight">
              Category Breakdown
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-2 font-data text-[10px] uppercase tracking-widest text-muted-foreground">Category</th>
                  <th className="text-center py-3 px-2 font-data text-[10px] uppercase tracking-widest text-muted-foreground">Products</th>
                  <th className="text-center py-3 px-2 font-data text-[10px] uppercase tracking-widest text-muted-foreground">TikTok</th>
                  <th className="text-center py-3 px-2 font-data text-[10px] uppercase tracking-widest text-muted-foreground">Amazon</th>
                  <th className="text-center py-3 px-2 font-data text-[10px] uppercase tracking-widest text-muted-foreground">Google</th>
                  <th className="text-center py-3 px-2 font-data text-[10px] uppercase tracking-widest text-muted-foreground">Cross-Platform</th>
                </tr>
              </thead>
              <tbody>
                {data.category_breakdown.map((cat, idx) => (
                  <tr key={cat.category} className="border-b border-border/50 hover:bg-card/50 transition-colors" data-testid={`cat-row-${idx}`}>
                    <td className="py-3 px-2 font-medium">{cat.category}</td>
                    <td className="text-center py-3 px-2 font-data text-muted-foreground">{cat.product_count}</td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-data font-bold ${scoreColor(cat.avg_tiktok)}`}>{cat.avg_tiktok}</span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-data font-bold ${scoreColor(cat.avg_amazon)}`}>{cat.avg_amazon}</span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-data font-bold ${scoreColor(cat.avg_google)}`}>{cat.avg_google}</span>
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className={`font-data font-bold ${scoreColor(cat.avg_cross_platform)}`}>{cat.avg_cross_platform}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Arbitrage Opportunities */}
        <div className="glass p-6" data-testid="arbitrage-opportunities">
          <div className="flex items-center gap-3 mb-2">
            <Target className="w-5 h-5 text-status-explosive" />
            <h2 className="font-heading text-xl font-bold uppercase tracking-tight">
              Arbitrage Opportunities
            </h2>
          </div>
          {beginnerMode && (
            <p className="text-sm text-muted-foreground mb-6">
              Products with high TikTok demand but lower Amazon presence. These represent untapped
              markets where you can capture demand before competitors.
            </p>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.top_arbitrage_opportunities.slice(0, 9).map((opp, idx) => (
              <div
                key={opp.id}
                className="p-4 bg-card border border-border hover:border-primary/30 transition-colors cursor-pointer"
                onClick={() => navigate(`/product/${opp.id}`)}
                data-testid={`arbitrage-${idx}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-sm font-medium truncate max-w-[200px]">{opp.name}</h4>
                  <Badge
                    className={`text-[9px] font-data flex-shrink-0 ml-2 ${
                      opp.status === "EXPLOSIVE"
                        ? "bg-status-explosive/10 text-status-explosive border-status-explosive/30"
                        : opp.status === "RISING"
                        ? "bg-status-rising/10 text-status-rising border-status-rising/30"
                        : "bg-status-early/10 text-status-early border-status-early/30"
                    }`}
                    variant="outline"
                  >
                    {opp.status.replace("_", " ")}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-3">{opp.category} &middot; ${opp.price?.toFixed(2)}</p>

                {/* Platform scores */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Zap className="w-3 h-3" /> TikTok
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1 bg-card border border-border overflow-hidden">
                        <div className={`h-full ${scoreBg(opp.tiktok_demand)}`} style={{ width: `${opp.tiktok_demand}%` }} />
                      </div>
                      <span className={`font-data text-xs font-bold ${scoreColor(opp.tiktok_demand)}`}>{opp.tiktok_demand}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <ShoppingBag className="w-3 h-3" /> Amazon
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1 bg-card border border-border overflow-hidden">
                        <div className={`h-full ${scoreBg(opp.amazon_demand)}`} style={{ width: `${opp.amazon_demand}%` }} />
                      </div>
                      <span className={`font-data text-xs font-bold ${scoreColor(opp.amazon_demand)}`}>{opp.amazon_demand}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" /> Google
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1 bg-card border border-border overflow-hidden">
                        <div className={`h-full ${scoreBg(opp.google_trends)}`} style={{ width: `${opp.google_trends}%` }} />
                      </div>
                      <span className={`font-data text-xs font-bold ${scoreColor(opp.google_trends)}`}>{opp.google_trends}</span>
                    </div>
                  </div>
                </div>

                {/* Arbitrage gap */}
                <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
                  <span className="text-[10px] text-muted-foreground uppercase">Arbitrage Gap</span>
                  <span className={`font-data text-sm font-bold flex items-center gap-1 ${opp.arbitrage_gap > 0 ? "text-status-explosive" : "text-status-avoid"}`}>
                    {opp.arbitrage_gap > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {opp.arbitrage_gap > 0 ? "+" : ""}{opp.arbitrage_gap}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default MarketInsights;
