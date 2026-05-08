import React from "react";
import { useApp } from "../App";
import { Progress } from "./ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import {
  Zap,
  Users,
  MessageSquare,
  Target,
  Globe,
  Shield,
  Repeat,
} from "lucide-react";

const ScoreBreakdown = ({ breakdown }) => {
  const { beginnerMode } = useApp();

  const scores = [
    {
      key: "velocity_score",
      label: "Velocity",
      icon: Zap,
      value: breakdown.velocity_score,
      weight: "25%",
      tooltip: "Sales growth rate over time. Higher = faster growth.",
    },
    {
      key: "creator_adoption_score",
      label: "Creator Adoption",
      icon: Users,
      value: breakdown.creator_adoption_score,
      weight: "20%",
      tooltip: "Number of unique creators posting about this product.",
    },
    {
      key: "engagement_quality_score",
      label: "Engagement Quality",
      icon: MessageSquare,
      value: breakdown.engagement_quality_score,
      weight: "15%",
      tooltip: "Comments vs likes ratio, indicating buying intent.",
    },
    {
      key: "hook_strength_score",
      label: "Hook Strength",
      icon: Target,
      value: breakdown.hook_strength_score,
      weight: "10%",
      tooltip: "Pattern recognition from viral video hooks.",
    },
    {
      key: "market_expansion_score",
      label: "Market Expansion",
      icon: Globe,
      value: breakdown.market_expansion_score,
      weight: "10%",
      tooltip: "Cross-platform presence (Amazon, Google Trends).",
    },
    {
      key: "saturation_risk_score",
      label: "Saturation Risk",
      icon: Shield,
      value: 100 - breakdown.saturation_risk_score, // Invert for display
      weight: "10%",
      tooltip: "Lower saturation = better opportunity. Displayed inverted.",
      inverted: true,
    },
    {
      key: "repeatability_score",
      label: "Repeatability",
      icon: Repeat,
      value: breakdown.repeatability_score,
      weight: "10%",
      tooltip: "Are creators reposting with variations?",
    },
  ];

  const getProgressColor = (value) => {
    if (value >= 75) return "bg-status-explosive";
    if (value >= 50) return "bg-status-rising";
    if (value >= 25) return "bg-status-watchlist";
    return "bg-status-avoid";
  };

  const ScoreRow = ({ score }) => {
    const content = (
      <div className="flex items-center gap-4 p-3 bg-card border border-border hover:border-primary/30 transition-colors">
        <div className="p-2 bg-background border border-border">
          <score.icon className="w-4 h-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium truncate">{score.label}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground font-data">
                ({score.weight})
              </span>
              <span className={`font-data font-bold ${
                score.value >= 75 ? "status-explosive" :
                score.value >= 50 ? "status-rising" :
                score.value >= 25 ? "status-watchlist" : "status-avoid"
              }`}>
                {Math.round(score.value)}
              </span>
            </div>
          </div>
          <div className="h-2 bg-background border border-border overflow-hidden">
            <div 
              className={`h-full ${getProgressColor(score.value)} transition-all duration-500`}
              style={{ width: `${score.value}%` }}
            />
          </div>
        </div>
      </div>
    );

    if (beginnerMode) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>{content}</TooltipTrigger>
            <TooltipContent side="left" className="max-w-xs">
              <p className="font-semibold mb-1">{score.label}</p>
              <p className="text-sm">{score.tooltip}</p>
              {score.inverted && (
                <p className="text-xs text-muted-foreground mt-1">
                  Note: This score is inverted (100 - actual value) because lower saturation is better.
                </p>
              )}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    return content;
  };

  return (
    <div className="glass p-6" data-testid="score-breakdown">
      <h3 className="font-heading text-xl font-bold uppercase tracking-tight mb-4">
        Alpha Score Breakdown
      </h3>
      {beginnerMode && (
        <p className="text-sm text-muted-foreground mb-4">
          The Alpha Score is calculated from these 7 weighted factors. 
          Hover over each for more details.
        </p>
      )}
      <div className="space-y-2">
        {scores.map((score) => (
          <ScoreRow key={score.key} score={score} />
        ))}
      </div>
    </div>
  );
};

export default ScoreBreakdown;
