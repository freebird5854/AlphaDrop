import React from "react";
import { useApp } from "../App";
import { Progress } from "./ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import { Globe, ShoppingBag, TrendingUp, Zap } from "lucide-react";

const MarketValidation = ({ data }) => {
  const { beginnerMode } = useApp();

  const getScoreColor = (value) => {
    if (value >= 75) return "status-explosive";
    if (value >= 50) return "status-rising";
    if (value >= 25) return "status-watchlist";
    return "status-avoid";
  };

  const platforms = [
    {
      key: "tiktok_demand",
      label: "TikTok Shop",
      icon: Zap,
      value: data.tiktok_demand,
      description: "Demand level on TikTok Shop",
    },
    {
      key: "amazon_demand",
      label: "Amazon",
      icon: ShoppingBag,
      value: data.amazon_demand,
      description: "Search and sales demand on Amazon",
    },
    {
      key: "google_trends",
      label: "Google Trends",
      icon: TrendingUp,
      value: data.google_trends,
      description: "Search interest on Google",
    },
  ];

  return (
    <div className="glass p-6" data-testid="market-validation">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-accent/10 border border-accent/20">
          <Globe className="w-5 h-5 text-accent" />
        </div>
        <div>
          <h3 className="font-heading text-xl font-bold uppercase tracking-tight">
            Market Validation
          </h3>
          {beginnerMode && (
            <p className="text-sm text-muted-foreground">
              Cross-platform demand analysis
            </p>
          )}
        </div>
      </div>

      {beginnerMode && (
        <p className="text-sm text-muted-foreground mb-4">
          Products that show demand across multiple platforms are more likely to be winners. 
          High scores on all platforms = strong market validation.
        </p>
      )}

      {/* Cross-platform Score */}
      <div className="p-4 bg-card border border-border mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Cross-Platform Score</span>
          <span className={`font-data text-2xl font-bold ${getScoreColor(data.cross_platform_score)}`}>
            {data.cross_platform_score}
          </span>
        </div>
        <div className="h-2 bg-background border border-border overflow-hidden">
          <div
            className={`h-full ${
              data.cross_platform_score >= 75 ? "bg-status-explosive" :
              data.cross_platform_score >= 50 ? "bg-status-rising" :
              data.cross_platform_score >= 25 ? "bg-status-watchlist" : "bg-status-avoid"
            } transition-all duration-500`}
            style={{ width: `${data.cross_platform_score}%` }}
          />
        </div>
        {beginnerMode && (
          <p className="text-xs text-muted-foreground mt-2">
            Combined demand probability across all platforms
          </p>
        )}
      </div>

      {/* Platform Breakdown */}
      <div className="space-y-3">
        {platforms.map((platform) => (
          <div
            key={platform.key}
            className="flex items-center gap-3 p-3 bg-card border border-border"
          >
            <div className="p-1.5 bg-background border border-border">
              <platform.icon className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm">{platform.label}</span>
                <span className={`font-data font-bold ${getScoreColor(platform.value)}`}>
                  {platform.value}
                </span>
              </div>
              <div className="h-1.5 bg-background border border-border overflow-hidden">
                <div
                  className={`h-full ${
                    platform.value >= 75 ? "bg-status-explosive" :
                    platform.value >= 50 ? "bg-status-rising" :
                    platform.value >= 25 ? "bg-status-watchlist" : "bg-status-avoid"
                  } transition-all duration-500`}
                  style={{ width: `${platform.value}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketValidation;
