import React from "react";
import { useApp } from "../App";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Legend,
} from "recharts";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { TrendingUp, Activity, Users, ShoppingCart } from "lucide-react";

const TrendChart = ({ data }) => {
  const { beginnerMode } = useApp();

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="glass-heavy p-3 border border-border">
        <p className="font-data text-xs text-muted-foreground mb-2">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-2 h-2"
              style={{ backgroundColor: entry.color }}
            />
            <span className="font-data text-sm">
              {entry.name}: {entry.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const chartConfig = {
    sales: { color: "#00FF94", label: "Sales" },
    views: { color: "#00F0FF", label: "Views" },
    creators: { color: "#FFFF00", label: "Creators" },
    engagement: { color: "#FF5C00", label: "Engagement %" },
  };

  const chartComponent = (dataKey, color, label) => (
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{ fill: "#888", fontSize: 10, fontFamily: "JetBrains Mono" }}
          tickFormatter={(value) => new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fill: "#888", fontSize: 10, fontFamily: "JetBrains Mono" }}
          tickFormatter={(value) => {
            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
            if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
            return value;
          }}
        />
        <RechartsTooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          strokeWidth={2}
          fill={`url(#gradient-${dataKey})`}
          name={label}
        />
      </AreaChart>
    </ResponsiveContainer>
  );

  const content = (
    <div className="glass p-6" data-testid="trend-chart">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-heading text-xl font-bold uppercase tracking-tight">
          Trend Velocity
        </h3>
        <div className="flex items-center gap-2 text-muted-foreground">
          <TrendingUp className="w-4 h-4" />
          <span className="font-data text-xs uppercase">14 Day Trend</span>
        </div>
      </div>
      
      {beginnerMode && (
        <p className="text-sm text-muted-foreground mb-4">
          These charts show how the product's key metrics have changed over the past 14 days. 
          Look for acceleration (steep upward curves) as a sign of viral potential.
        </p>
      )}

      <Tabs defaultValue="sales" className="w-full">
        <TabsList className="bg-card border border-border mb-4">
          <TabsTrigger value="sales" className="font-data text-xs uppercase data-[state=active]:bg-primary data-[state=active]:text-black" data-testid="chart-tab-sales">
            <ShoppingCart className="w-3 h-3 mr-1" /> Sales
          </TabsTrigger>
          <TabsTrigger value="views" className="font-data text-xs uppercase data-[state=active]:bg-accent data-[state=active]:text-black" data-testid="chart-tab-views">
            <Activity className="w-3 h-3 mr-1" /> Views
          </TabsTrigger>
          <TabsTrigger value="creators" className="font-data text-xs uppercase data-[state=active]:bg-status-rising data-[state=active]:text-black" data-testid="chart-tab-creators">
            <Users className="w-3 h-3 mr-1" /> Creators
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sales" className="mt-0">
          {chartComponent("sales", "#00FF94", "Sales")}
        </TabsContent>
        <TabsContent value="views" className="mt-0">
          {chartComponent("views", "#00F0FF", "Views")}
        </TabsContent>
        <TabsContent value="creators" className="mt-0">
          {chartComponent("creators", "#FFFF00", "Creators")}
        </TabsContent>
      </Tabs>
    </div>
  );

  return content;
};

export default TrendChart;
