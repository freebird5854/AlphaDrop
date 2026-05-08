import React from "react";
import { useApp } from "../App";
import { Badge } from "./ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import { Target, Lightbulb } from "lucide-react";

const HookAnalysis = ({ hooks }) => {
  const { beginnerMode } = useApp();

  const getEffectivenessColor = (value) => {
    if (value >= 80) return "status-explosive";
    if (value >= 60) return "status-rising";
    return "status-watchlist";
  };

  const getEffectivenessBg = (value) => {
    if (value >= 80) return "bg-status-explosive/10 border-status-explosive/30";
    if (value >= 60) return "bg-status-rising/10 border-status-rising/30";
    return "bg-status-watchlist/10 border-status-watchlist/30";
  };

  return (
    <div className="glass p-6" data-testid="hook-analysis">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-primary/10 border border-primary/20">
          <Target className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-heading text-xl font-bold uppercase tracking-tight">
            Hook Intelligence
          </h3>
          {beginnerMode && (
            <p className="text-sm text-muted-foreground">
              Winning content angles used by top creators
            </p>
          )}
        </div>
      </div>

      {beginnerMode && (
        <div className="mb-4 p-3 bg-card border border-border">
          <div className="flex items-start gap-2">
            <Lightbulb className="w-4 h-4 text-primary mt-0.5" />
            <p className="text-sm text-muted-foreground">
              <span className="text-foreground font-medium">Pro Tip:</span> Use these proven hooks 
              as templates for your own content. The higher the effectiveness score, the more likely 
              the angle will resonate with viewers.
            </p>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {hooks.map((hook, index) => (
          <div
            key={index}
            className="p-4 bg-card border border-border hover:border-primary/30 transition-colors"
            data-testid={`hook-item-${index}`}
          >
            <div className="flex items-start justify-between gap-4 mb-2">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="font-data text-xs uppercase">
                  {hook.hook_type}
                </Badge>
              </div>
              <div className={`px-2 py-1 border ${getEffectivenessBg(hook.effectiveness)}`}>
                <span className={`font-data font-bold ${getEffectivenessColor(hook.effectiveness)}`}>
                  {hook.effectiveness}%
                </span>
              </div>
            </div>
            
            <p className="text-sm text-muted-foreground mb-3">
              {hook.description}
            </p>

            <div className="space-y-1">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
                Example Hooks:
              </p>
              {hook.examples.map((example, i) => (
                <div
                  key={i}
                  className="text-sm p-2 bg-background border-l-2 border-primary/50 pl-3 italic"
                >
                  "{example}"
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HookAnalysis;
