import React from "react";
import { useApp } from "../App";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";

const AlphaScoreGauge = ({ score, size = "default" }) => {
  const { beginnerMode } = useApp();

  const getColor = (score) => {
    if (score >= 80) return { stroke: "#00FF94", glow: "rgba(0, 255, 148, 0.3)" };
    if (score >= 60) return { stroke: "#FFFF00", glow: "rgba(255, 255, 0, 0.3)" };
    if (score >= 45) return { stroke: "#00F0FF", glow: "rgba(0, 240, 255, 0.3)" };
    if (score >= 40) return { stroke: "#FF5C00", glow: "rgba(255, 92, 0, 0.3)" };
    return { stroke: "#FF3B30", glow: "rgba(255, 59, 48, 0.3)" };
  };

  const getLabel = (score) => {
    if (score >= 80) return "EXPLOSIVE";
    if (score >= 60) return "BUILD POSITION";
    if (score >= 45) return "EARLY SIGNAL";
    if (score >= 40) return "WATCHLIST";
    return "AVOID";
  };

  const dimensions = {
    default: { size: 120, strokeWidth: 8, fontSize: "text-3xl", labelSize: "text-[10px]" },
    large: { size: 180, strokeWidth: 10, fontSize: "text-5xl", labelSize: "text-xs" },
    small: { size: 80, strokeWidth: 6, fontSize: "text-xl", labelSize: "text-[8px]" },
  };

  const dim = dimensions[size];
  const radius = (dim.size - dim.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const colors = getColor(score);
  const label = getLabel(score);

  const gauge = (
    <div 
      className="relative flex items-center justify-center"
      style={{ width: dim.size, height: dim.size }}
      data-testid="alpha-score-gauge"
    >
      {/* Background circle */}
      <svg
        className="absolute inset-0"
        width={dim.size}
        height={dim.size}
        viewBox={`0 0 ${dim.size} ${dim.size}`}
      >
        <circle
          cx={dim.size / 2}
          cy={dim.size / 2}
          r={radius}
          fill="none"
          stroke="hsl(0 0% 13%)"
          strokeWidth={dim.strokeWidth}
        />
      </svg>

      {/* Progress circle */}
      <svg
        className="absolute inset-0 alpha-score-ring"
        width={dim.size}
        height={dim.size}
        viewBox={`0 0 ${dim.size} ${dim.size}`}
        style={{ filter: `drop-shadow(0 0 10px ${colors.glow})` }}
      >
        <circle
          cx={dim.size / 2}
          cy={dim.size / 2}
          r={radius}
          fill="none"
          stroke={colors.stroke}
          strokeWidth={dim.strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>

      {/* Score text */}
      <div className="text-center z-10">
        <span 
          className={`font-data font-bold ${dim.fontSize}`}
          style={{ color: colors.stroke }}
        >
          {score}
        </span>
        <p className={`${dim.labelSize} text-muted-foreground uppercase tracking-widest mt-1`}>
          Alpha
        </p>
      </div>
    </div>
  );

  if (beginnerMode) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex flex-col items-center gap-2">
              {gauge}
              <span 
                className={`font-data ${dim.labelSize} font-bold uppercase tracking-wider`}
                style={{ color: colors.stroke }}
              >
                {label}
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <p className="font-semibold mb-2">Alpha Score: {score}/100</p>
            <p className="text-sm">
              The Alpha Score combines 7 key factors: velocity, creator adoption, 
              engagement quality, hook strength, market expansion, saturation risk, 
              and repeatability to predict viral potential.
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <div className="flex flex-col items-center gap-2">
      {gauge}
      <span 
        className={`font-data ${dim.labelSize} font-bold uppercase tracking-wider`}
        style={{ color: colors.stroke }}
      >
        {label}
      </span>
    </div>
  );
};

export default AlphaScoreGauge;
