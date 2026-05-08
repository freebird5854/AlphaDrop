import React from "react";
import { useApp } from "../App";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import {
  Eye,
  Heart,
  MessageCircle,
  Share2,
  Play,
  Clock,
} from "lucide-react";

const TopVideos = ({ videos }) => {
  const { beginnerMode } = useApp();

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  return (
    <div className="glass p-6" data-testid="top-videos">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-destructive/10 border border-destructive/20">
          <Play className="w-5 h-5 text-destructive" />
        </div>
        <div>
          <h3 className="font-heading text-xl font-bold uppercase tracking-tight">
            Top Performing Videos
          </h3>
          {beginnerMode && (
            <p className="text-sm text-muted-foreground">
              Analyze what's working
            </p>
          )}
        </div>
      </div>

      {beginnerMode && (
        <p className="text-sm text-muted-foreground mb-4">
          Study these top videos to understand what content styles and hooks are driving engagement. 
          Look for patterns you can replicate.
        </p>
      )}

      <ScrollArea className="h-[400px] pr-4">
        <div className="space-y-3">
          {videos.map((video, index) => (
            <div
              key={video.id}
              className="p-4 bg-card border border-border hover:border-primary/30 transition-colors"
              data-testid={`video-item-${index}`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <Badge variant="outline" className="font-data text-xs">
                  #{index + 1}
                </Badge>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  <span className="font-data text-xs">
                    {video.posted_days_ago}d ago
                  </span>
                </div>
              </div>

              {/* Creator */}
              <p className="font-data text-sm text-primary mb-2">
                {video.creator}
              </p>

              {/* Hook */}
              <p className="text-sm italic text-muted-foreground mb-3 border-l-2 border-primary/50 pl-2">
                "{video.hook}"
              </p>

              {/* Stats */}
              <div className="grid grid-cols-4 gap-2">
                <div className="text-center p-2 bg-background border border-border">
                  <Eye className="w-3 h-3 mx-auto mb-1 text-muted-foreground" />
                  <p className="font-data text-xs font-bold">
                    {formatNumber(video.views)}
                  </p>
                </div>
                <div className="text-center p-2 bg-background border border-border">
                  <Heart className="w-3 h-3 mx-auto mb-1 text-status-avoid" />
                  <p className="font-data text-xs font-bold">
                    {formatNumber(video.likes)}
                  </p>
                </div>
                <div className="text-center p-2 bg-background border border-border">
                  <MessageCircle className="w-3 h-3 mx-auto mb-1 text-status-early" />
                  <p className="font-data text-xs font-bold">
                    {formatNumber(video.comments)}
                  </p>
                </div>
                <div className="text-center p-2 bg-background border border-border">
                  <Share2 className="w-3 h-3 mx-auto mb-1 text-status-rising" />
                  <p className="font-data text-xs font-bold">
                    {formatNumber(video.shares)}
                  </p>
                </div>
              </div>

              {/* Engagement Rate */}
              <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Engagement Rate</span>
                <span className="font-data text-sm font-bold status-explosive">
                  {(((video.likes + video.comments) / video.views) * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

export default TopVideos;
