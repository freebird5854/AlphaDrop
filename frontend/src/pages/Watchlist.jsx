import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Skeleton } from "../components/ui/skeleton";
import {
  Bookmark,
  Trash2,
  ExternalLink,
  FileText,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import { toast } from "sonner";

const Watchlist = () => {
  const navigate = useNavigate();
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [watchlist, setWatchlist] = useState([]);
  
  // For demo purposes, using a simple user ID
  const userId = localStorage.getItem("alpha_user_id") || (() => {
    const id = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("alpha_user_id", id);
    return id;
  })();

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = async () => {
    try {
      setLoading(true);
      const res = await api.getWatchlist(userId);
      setWatchlist(res.data.watchlist);
    } catch (e) {
      console.error("Failed to load watchlist:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (productId) => {
    try {
      await api.removeFromWatchlist(userId, productId);
      setWatchlist(watchlist.filter(item => item.product_id !== productId));
      toast.success("Removed from watchlist");
    } catch (e) {
      toast.error("Failed to remove from watchlist");
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      EXPLOSIVE: "bg-status-explosive text-black",
      RISING: "bg-status-rising text-black",
      EARLY_SIGNAL: "bg-status-early text-black",
      WATCHLIST: "bg-status-watchlist text-black",
      AVOID: "bg-status-avoid text-white",
    };
    return colors[status] || "bg-muted";
  };

  const getScoreColor = (score) => {
    if (score >= 72) return "text-status-explosive";
    if (score >= 58) return "text-status-rising";
    if (score >= 45) return "text-status-early";
    return "text-status-watchlist";
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="watchlist-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-4xl font-black tracking-tighter uppercase">
              <span className="text-primary">My</span> Watchlist
            </h1>
            {beginnerMode && (
              <p className="text-muted-foreground mt-2 max-w-xl">
                Products you're monitoring. Click the bookmark icon on any product to add it here.
              </p>
            )}
          </div>
          <Badge variant="outline" className="font-data">
            {watchlist.length} products
          </Badge>
        </div>

        {/* Watchlist Items */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-24 bg-card" />
            ))}
          </div>
        ) : watchlist.length === 0 ? (
          <div className="glass p-12 text-center">
            <Bookmark className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-heading text-xl font-bold uppercase mb-2">
              No Products Saved
            </h3>
            <p className="text-muted-foreground mb-6">
              Add products to your watchlist by clicking the bookmark icon on any product card
            </p>
            <Button onClick={() => navigate("/discover")} variant="outline">
              Discover Products
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {watchlist.map((item, index) => (
              <div
                key={item.id}
                className="glass p-4 flex items-center gap-4 animate-slide-up opacity-0"
                style={{ animationDelay: `${index * 0.05}s` }}
                data-testid={`watchlist-item-${item.product_id}`}
              >
                {/* Product Image */}
                <div className="w-16 h-16 bg-card border border-border overflow-hidden flex-shrink-0">
                  {item.product_image ? (
                    <img
                      src={item.product_image}
                      alt={item.product_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <FileText className="w-6 h-6 text-muted-foreground" />
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge className={`${getStatusColor(item.status)} font-data text-[10px]`}>
                      {item.status.replace("_", " ")}
                    </Badge>
                    <span className={`font-data font-bold ${getScoreColor(item.alpha_score)}`}>
                      {item.alpha_score}
                    </span>
                  </div>
                  <h3 className="font-medium truncate">{item.product_name}</h3>
                  {item.notes && (
                    <p className="text-sm text-muted-foreground truncate">{item.notes}</p>
                  )}
                  <p className="text-xs text-muted-foreground font-data mt-1">
                    Added {new Date(item.added_at).toLocaleDateString()}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/product/${item.product_id}`)}
                    data-testid={`view-${item.product_id}`}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemove(item.product_id)}
                    className="text-status-avoid hover:text-status-avoid hover:bg-status-avoid/10"
                    data-testid={`remove-${item.product_id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Beginner Tip */}
        {beginnerMode && watchlist.length > 0 && (
          <div className="glass-heavy p-6 border-l-4 border-accent">
            <h3 className="font-heading text-lg font-bold uppercase mb-2">
              Pro Tip
            </h3>
            <p className="text-muted-foreground text-sm">
              Check your watchlist daily to monitor Alpha Score changes. 
              When a product moves from "Early Signal" to "Rising" or "Explosive", 
              it's time to take action. Products can shift status within 24-48 hours.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Watchlist;
