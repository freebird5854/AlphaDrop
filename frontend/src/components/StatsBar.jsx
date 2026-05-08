import React from "react";
import { useApp } from "../App";
import { Skeleton } from "./ui/skeleton";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import {
  Package,
  Flame,
  TrendingUp,
  Eye,
  Activity,
  Tag,
} from "lucide-react";

const StatsBar = ({ stats, loading }) => {
  const { beginnerMode } = useApp();

  if (loading || !stats) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-24 bg-card" />
        ))}
      </div>
    );
  }

  const statItems = [
    {
      icon: Package,
      label: "Products Tracked",
      value: stats.total_products_tracked,
      color: "text-foreground",
      tooltip: "Total number of products being monitored in the system",
    },
    {
      icon: Flame,
      label: "Explosive",
      value: stats.explosive_count,
      color: "status-explosive",
      tooltip: "Products with Alpha Score 80+ showing viral potential",
    },
    {
      icon: TrendingUp,
      label: "Rising",
      value: stats.rising_count,
      color: "status-rising",
      tooltip: "Products with steady growth patterns (score 60-79)",
    },
    {
      icon: Eye,
      label: "Early Signals",
      value: stats.early_signal_count,
      color: "status-early",
      tooltip: "Products showing pre-viral accumulation patterns",
    },
    {
      icon: Activity,
      label: "Avg Alpha Score",
      value: stats.avg_alpha_score,
      color: "text-primary",
      tooltip: "Average Alpha Score across all tracked products",
    },
    {
      icon: Tag,
      label: "Top Category",
      value: stats.top_category.split(" ")[0],
      color: "text-accent",
      tooltip: `Most active category: ${stats.top_category}`,
    },
  ];

  const StatItem = ({ item }) => {
    const content = (
      <div className="glass p-4 border-l-2 border-transparent hover:border-primary transition-colors" data-testid={`stat-${item.label.toLowerCase().replace(/\s/g, '-')}`}>
        <div className="flex items-center gap-3">
          <div className={`p-2 bg-card border border-border ${item.color}`}>
            <item.icon className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest">
              {item.label}
            </p>
            <p className={`font-data text-xl font-bold ${item.color}`}>
              {typeof item.value === "number" && item.label !== "Avg Alpha Score"
                ? item.value.toLocaleString()
                : item.value}
            </p>
          </div>
        </div>
      </div>
    );

    if (beginnerMode) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>{content}</TooltipTrigger>
            <TooltipContent side="bottom">
              <p>{item.tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    return content;
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4" data-testid="stats-bar">
      {statItems.map((item, index) => (
        <div
          key={item.label}
          className={`animate-slide-up opacity-0 stagger-${index + 1}`}
        >
          <StatItem item={item} />
        </div>
      ))}
    </div>
  );
};

export default StatsBar;
