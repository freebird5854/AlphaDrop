import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import {
  Target,
  Zap,
  TrendingUp,
  Eye,
  Users,
  Play,
  Heart,
  MessageCircle,
  ArrowRight,
  Flame,
  Sparkles,
  Brain,
} from "lucide-react";

const HookIntelligence = () => {
  const navigate = useNavigate();
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState("hooks");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await api.getHookIntelligence();
      setData(res.data);
    } catch (e) {
      console.error("Failed to load hook intelligence:", e);
    } finally {
      setLoading(false);
    }
  };

  const getEffColor = (val) => {
    if (val >= 80) return "text-status-explosive";
    if (val >= 65) return "text-status-rising";
    return "text-status-early";
  };

  const getEffBg = (val) => {
    if (val >= 80) return "bg-status-explosive";
    if (val >= 65) return "bg-status-rising";
    return "bg-status-early";
  };

  const formatNum = (n) => {
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
    return String(n);
  };

  const tabs = [
    { id: "hooks", label: "Hook Types", icon: Target },
    { id: "triggers", label: "Emotional Triggers", icon: Brain },
    { id: "videos", label: "Top Videos", icon: Play },
  ];

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6" data-testid="hook-intelligence-loading">
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
          <p className="text-muted-foreground">Failed to load hook intelligence data.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8" data-testid="hook-intelligence-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary/10 border border-primary/30">
              <Target className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h1 className="font-heading text-3xl md:text-4xl font-black tracking-tighter uppercase leading-none">
                Hook <span className="text-primary">Intelligence</span>
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Winning content patterns from {data.total_products_analyzed} products &middot; {data.total_hooks_detected} hooks analyzed
              </p>
            </div>
          </div>
          {beginnerMode && (
            <div className="glass p-3 max-w-sm border-l-2 border-primary">
              <p className="text-xs text-muted-foreground">
                <span className="text-primary font-bold">TIP:</span> Hooks are the opening seconds
                of a video that grab attention. The best hooks match proven emotional triggers.
              </p>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-border pb-px">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 font-data text-xs uppercase tracking-wider transition-colors border-b-2 -mb-px ${
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
              data-testid={`tab-${tab.id}`}
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Hook Types Tab */}
        {activeTab === "hooks" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-testid="hooks-tab-content">
            {data.hook_types.map((hook, idx) => (
              <div key={hook.hook_type} className="glass p-5 space-y-4 group hover:border-primary/30 transition-colors" data-testid={`hook-type-${idx}`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 flex items-center justify-center bg-card border border-border font-data text-sm font-bold text-muted-foreground">
                      #{idx + 1}
                    </div>
                    <div>
                      <h3 className="font-heading text-lg font-bold uppercase tracking-tight">
                        {hook.hook_type}
                      </h3>
                      <p className="text-xs text-muted-foreground font-data">
                        {hook.total_uses} products &middot; max {hook.max_effectiveness}%
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`font-data text-2xl font-bold ${getEffColor(hook.avg_effectiveness)}`}>
                      {hook.avg_effectiveness}%
                    </span>
                    <p className="text-[10px] text-muted-foreground uppercase">avg eff.</p>
                  </div>
                </div>

                {/* Effectiveness bar */}
                <div className="h-1.5 bg-card border border-border overflow-hidden">
                  <div
                    className={`h-full ${getEffBg(hook.avg_effectiveness)} transition-all duration-700`}
                    style={{ width: `${hook.avg_effectiveness}%` }}
                  />
                </div>

                {/* Example hooks */}
                <div className="space-y-1.5">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-widest">Example Hooks</p>
                  {hook.examples.slice(0, 3).map((ex, i) => (
                    <div key={i} className="text-sm p-2 bg-card border-l-2 border-primary/40 pl-3 italic text-muted-foreground">
                      "{ex}"
                    </div>
                  ))}
                </div>

                {/* Top products using this hook */}
                {hook.top_products.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest">Top Products</p>
                    {hook.top_products.slice(0, 3).map((prod, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 bg-card border border-border hover:border-primary/20 cursor-pointer transition-colors"
                        onClick={() => navigate(`/product/${prod.id}`)}
                      >
                        <span className="text-xs truncate max-w-[200px]">{prod.name}</span>
                        <div className="flex items-center gap-2">
                          <Badge
                            className={`text-[9px] font-data ${
                              prod.status === "EXPLOSIVE"
                                ? "bg-status-explosive/10 text-status-explosive border-status-explosive/30"
                                : prod.status === "RISING"
                                ? "bg-status-rising/10 text-status-rising border-status-rising/30"
                                : "bg-status-early/10 text-status-early border-status-early/30"
                            }`}
                            variant="outline"
                          >
                            {prod.status.replace("_", " ")}
                          </Badge>
                          <span className={`font-data text-xs font-bold ${getEffColor(prod.effectiveness)}`}>
                            {prod.effectiveness}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Emotional Triggers Tab */}
        {activeTab === "triggers" && (
          <div className="space-y-6" data-testid="triggers-tab-content">
            {beginnerMode && (
              <div className="glass p-4 border-l-4 border-status-rising">
                <p className="text-sm text-muted-foreground">
                  <span className="text-status-rising font-bold">EMOTIONAL TRIGGERS</span> — Every viral video
                  taps into core human emotions. Understanding which triggers resonate helps you create
                  content that stops the scroll.
                </p>
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {data.emotional_triggers.map((trigger, idx) => (
                <div key={trigger.trigger} className="glass p-6 space-y-4 border-t-2 border-primary" data-testid={`trigger-${idx}`}>
                  <div className="flex items-center gap-3">
                    <Brain className={`w-6 h-6 ${idx === 0 ? "text-status-explosive" : idx === 1 ? "text-status-rising" : "text-primary"}`} />
                    <h3 className="font-heading text-lg font-bold uppercase tracking-tight">
                      {trigger.trigger}
                    </h3>
                  </div>
                  <div className="text-center py-4">
                    <span className={`font-data text-5xl font-bold ${getEffColor(trigger.power_score)}`}>
                      {trigger.power_score}
                    </span>
                    <p className="text-xs text-muted-foreground uppercase mt-1">Power Score</p>
                  </div>
                  <div className="h-1.5 bg-card border border-border overflow-hidden">
                    <div
                      className={`h-full ${getEffBg(trigger.power_score)} transition-all duration-700`}
                      style={{ width: `${trigger.power_score}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{trigger.count} products</span>
                    <div className="flex gap-1">
                      {trigger.hook_types.map((ht) => (
                        <Badge key={ht} variant="outline" className="text-[9px] font-data">{ht}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Videos Tab */}
        {activeTab === "videos" && (
          <div className="space-y-4" data-testid="videos-tab-content">
            {beginnerMode && (
              <div className="glass p-4 border-l-4 border-primary">
                <p className="text-sm text-muted-foreground">
                  <span className="text-primary font-bold">TOP PERFORMING VIDEOS</span> — These are the highest-performing
                  creator videos across tracked products. Study their hooks to replicate success.
                </p>
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.top_videos.map((video, idx) => (
                <div
                  key={idx}
                  className="glass p-4 flex gap-4 hover:border-primary/30 transition-colors cursor-pointer"
                  onClick={() => navigate(`/product/${video.product_id}`)}
                  data-testid={`top-video-${idx}`}
                >
                  <div className="w-10 h-10 flex items-center justify-center bg-card border border-border flex-shrink-0">
                    <Play className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{video.product_name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {video.creator} &middot; Alpha {video.alpha_score}
                    </p>
                    {video.hook && (
                      <p className="text-xs text-primary/80 italic mt-1 truncate">"{video.hook}"</p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Eye className="w-3 h-3" />
                        {formatNum(video.views)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="w-3 h-3" />
                        {formatNum(video.likes)}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="w-3 h-3" />
                        {formatNum(video.comments)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default HookIntelligence;
