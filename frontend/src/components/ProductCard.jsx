import React from "react";
import { useNavigate } from "react-router-dom";
import { useApp, api, getUserId } from "../App";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Users,
  ShoppingCart,
  Bookmark,
} from "lucide-react";
import { toast } from "sonner";

const ProductCard = ({ product }) => {
  const navigate = useNavigate();
  const { beginnerMode, loadWatchlistCount } = useApp();

  const handleAddToWatchlist = async (e) => {
    e.stopPropagation();
    try {
      await api.addToWatchlist(getUserId(), product.id);
      toast.success("Added to watchlist!");
      loadWatchlistCount();
    } catch (err) {
      if (err.response?.status === 400) {
        toast.info("Already in watchlist");
      } else {
        toast.error("Failed to add to watchlist");
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      EXPLOSIVE: "bg-status-explosive text-black",
      SCALING_NOW: "bg-status-explosive text-black",
      EXPLODING_SOON: "bg-primary text-black",
      RISING: "bg-status-rising text-black",
      EARLY_SIGNAL: "bg-status-early text-black",
      SATURATION_WARNING: "bg-status-avoid text-white",
      WATCHLIST: "bg-status-watchlist text-black",
      AVOID: "bg-status-avoid text-white",
    };
    return colors[status] || "bg-muted";
  };

  const getScoreColor = (score) => {
    if (score >= 72) return "text-status-explosive";
    if (score >= 58) return "text-status-rising";
    if (score >= 45) return "text-status-early";
    if (score >= 35) return "text-status-watchlist";
    return "text-status-avoid";
  };

  const getScoreBg = (score) => {
    if (score >= 72) return "bg-status-explosive/10 border-status-explosive/30";
    if (score >= 58) return "bg-status-rising/10 border-status-rising/30";
    if (score >= 45) return "bg-status-early/10 border-status-early/30";
    if (score >= 35) return "bg-status-watchlist/10 border-status-watchlist/30";
    return "bg-status-avoid/10 border-status-avoid/30";
  };

  const getTrendIcon = (direction) => {
    if (direction === "up") return <TrendingUp className="w-3 h-3" />;
    if (direction === "down") return <TrendingDown className="w-3 h-3" />;
    return <Minus className="w-3 h-3" />;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  const cardContent = (
    <div
      className="group relative bg-card border border-border card-hover cursor-pointer overflow-hidden"
      onClick={() => navigate(`/product/${product.id}`)}
      data-testid={`product-card-${product.id}`}
    >
      {/* Image */}
      <div className="relative aspect-square bg-black/50 overflow-hidden">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {/* Alpha Score Overlay */}
        <div className={`absolute top-2 right-2 p-2 border ${getScoreBg(product.alpha_score)}`}>
          <span className={`font-data text-xl font-bold ${getScoreColor(product.alpha_score)}`}>
            {product.alpha_score}
          </span>
        </div>
        {/* Status Badge */}
        <div className="absolute bottom-2 left-2">
          <Badge className={`${getStatusColor(product.status)} font-data text-[10px] font-bold uppercase tracking-wider px-2 py-0.5`}>
            {product.status.replace("_", " ")}
          </Badge>
        </div>
        {/* Watchlist Button */}
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-2 left-2 p-1.5 bg-black/50 hover:bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={handleAddToWatchlist}
          data-testid={`watchlist-btn-${product.id}`}
        >
          <Bookmark className="w-4 h-4 text-white" />
        </Button>
      </div>

      {/* Content */}
      <div className="p-3 space-y-2">
        {/* Category & Trend */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-data">
            {product.category}
          </span>
          <div className={`flex items-center gap-1 ${
            product.trend_direction === "up" ? "status-explosive" :
            product.trend_direction === "down" ? "status-avoid" : "text-muted-foreground"
          }`}>
            {getTrendIcon(product.trend_direction)}
          </div>
        </div>

        {/* Name & Price */}
        <div>
          <h3 className="font-heading text-sm font-bold uppercase tracking-tight line-clamp-1 group-hover:text-primary transition-colors">
            {product.name}
          </h3>
          <p className="font-data text-primary font-medium">
            ${product.price.toFixed(2)}
          </p>
        </div>

        {/* Stats */}
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

        {/* Reason (truncated) */}
        <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
          {product.reason}
        </p>

        {/* v2.0 Indicators */}
        {(product.momentum_multiplier > 1.1 || (product.saturation_countdown > 0 && product.saturation_countdown <= 30)) && (
          <div className="flex items-center gap-2 pt-1 border-t border-border/50">
            {product.momentum_multiplier > 1.1 && (
              <span className="text-[9px] font-data font-bold text-status-explosive bg-status-explosive/10 px-1.5 py-0.5">
                {product.momentum_multiplier}x MOM
              </span>
            )}
            {product.saturation_countdown > 0 && product.saturation_countdown <= 30 && (
              <span className="text-[9px] font-data font-bold text-status-avoid bg-status-avoid/10 px-1.5 py-0.5">
                {product.saturation_countdown}d LEFT
              </span>
            )}
            {product.entry_window && product.entry_window !== "open" && (
              <span className={`text-[9px] font-data font-bold px-1.5 py-0.5 ${
                product.entry_window === "optimal" ? "text-primary bg-primary/10" :
                product.entry_window === "closing" ? "text-status-rising bg-status-rising/10" :
                "text-status-avoid bg-status-avoid/10"
              }`}>
                {product.entry_window.toUpperCase()}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Hover Glow Effect */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        <div className={`absolute inset-0 ${
          product.status === "EXPLOSIVE" ? "bg-status-explosive/5" :
          product.status === "RISING" ? "bg-status-rising/5" :
          product.status === "EARLY_SIGNAL" ? "bg-status-early/5" : ""
        }`} />
      </div>
    </div>
  );

  if (beginnerMode) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>{cardContent}</TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <p className="font-semibold mb-1">Alpha Score: {product.alpha_score}</p>
            <p className="text-sm">
              {product.alpha_score >= 72 && "This product is showing explosive potential. Consider testing immediately."}
              {product.alpha_score >= 58 && product.alpha_score < 72 && "Steady growth detected. Good for building a position over time."}
              {product.alpha_score >= 45 && product.alpha_score < 58 && "Early signals detected. Add to watchlist and monitor."}
              {product.alpha_score < 45 && "Not recommended. Focus on higher-scoring products."}
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return cardContent;
};

export default ProductCard;
