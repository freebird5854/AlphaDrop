import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import AlphaScoreGauge from "../components/AlphaScoreGauge";
import ScoreBreakdown from "../components/ScoreBreakdown";
import TrendChart from "../components/TrendChart";
import HookAnalysis from "../components/HookAnalysis";
import MarketValidation from "../components/MarketValidation";
import TopVideos from "../components/TopVideos";
import { Skeleton } from "../components/ui/skeleton";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../components/ui/tooltip";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  Users,
  Eye,
  ShoppingCart,
  Activity,
  AlertTriangle,
  ExternalLink,
} from "lucide-react";
import { toast } from "sonner";

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [product, setProduct] = useState(null);

  useEffect(() => {
    loadProduct();
  }, [id]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const res = await api.getProduct(id);
      setProduct(res.data);
    } catch (e) {
      console.error("Failed to load product:", e);
      toast.error("Product not found");
      navigate("/");
    } finally {
      setLoading(false);
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

  const getStatusLabel = (status) => {
    const labels = {
      EXPLOSIVE: "ENTER NOW",
      RISING: "BUILD POSITION",
      EARLY_SIGNAL: "EARLY SIGNAL",
      WATCHLIST: "WATCHLIST",
      AVOID: "AVOID",
    };
    return labels[status] || status;
  };

  const getTrendIcon = (direction) => {
    if (direction === "up") return <TrendingUp className="w-5 h-5 status-explosive" />;
    if (direction === "down") return <TrendingDown className="w-5 h-5 status-avoid" />;
    return <Minus className="w-5 h-5 text-muted-foreground" />;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <Skeleton className="h-12 w-48 bg-card" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Skeleton className="h-96 bg-card lg:col-span-2" />
            <Skeleton className="h-96 bg-card" />
          </div>
        </div>
      </Layout>
    );
  }

  if (!product) return null;

  const StatCard = ({ icon: Icon, label, value, tooltip }) => {
    const content = (
      <div className="glass p-4 flex items-center gap-4">
        <div className="p-2 bg-primary/10 border border-primary/20">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
          <p className="font-data text-xl font-bold">{value}</p>
        </div>
      </div>
    );

    if (beginnerMode && tooltip) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>{content}</TooltipTrigger>
            <TooltipContent side="bottom" className="max-w-xs">
              <p>{tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    return content;
  };

  return (
    <Layout>
      <div className="space-y-8" data-testid="product-detail-page">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="font-data text-sm uppercase tracking-wider"
          data-testid="back-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Button>

        {/* Header */}
        <div className="glass p-6 lg:p-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Product Image */}
            <div className="w-full lg:w-64 h-64 bg-card border border-border overflow-hidden flex-shrink-0">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-full object-cover"
                data-testid="product-image"
              />
            </div>

            {/* Product Info */}
            <div className="flex-1 space-y-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <Badge className={`${getStatusColor(product.status)} font-data text-xs font-bold uppercase tracking-wider`}>
                      {getStatusLabel(product.status)}
                    </Badge>
                    <Badge variant="outline" className="font-data text-xs">
                      {product.category}
                    </Badge>
                  </div>
                  <h1 className="font-heading text-3xl lg:text-4xl font-black tracking-tight uppercase" data-testid="product-name">
                    {product.name}
                  </h1>
                  <p className="font-data text-2xl font-bold text-primary mt-2">
                    ${product.price.toFixed(2)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {getTrendIcon(product.trend_direction)}
                  <span className="font-data text-sm text-muted-foreground uppercase">
                    {product.trend_direction}
                  </span>
                </div>
              </div>

              {/* Reason */}
              <div className="p-4 bg-card border-l-2 border-primary">
                <p className="font-data text-sm text-muted-foreground uppercase tracking-wider mb-1">
                  Why it's trending
                </p>
                <p className="text-foreground" data-testid="product-reason">{product.reason}</p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  icon={ShoppingCart}
                  label="Total Sales"
                  value={formatNumber(product.total_sales)}
                  tooltip="Total units sold across all tracked TikTok Shop listings in the past 14 days"
                />
                <StatCard
                  icon={Eye}
                  label="Total Views"
                  value={formatNumber(product.total_views)}
                  tooltip="Combined video views from all creators promoting this product"
                />
                <StatCard
                  icon={Users}
                  label="Creators"
                  value={product.creator_count}
                  tooltip="Number of unique TikTok creators currently promoting this product"
                />
                <StatCard
                  icon={Activity}
                  label="Avg Engagement"
                  value={`${product.avg_engagement}%`}
                  tooltip="Average engagement rate (likes + comments / views) across all videos"
                />
              </div>

              {/* Risk Level */}
              <div className="flex items-center gap-4 p-4 bg-card border border-border">
                <AlertTriangle className={`w-5 h-5 ${
                  product.risk_level === "low" ? "status-explosive" :
                  product.risk_level === "medium" ? "status-rising" : "status-avoid"
                }`} />
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Risk Level</p>
                  <p className="font-data font-bold uppercase">{product.risk_level}</p>
                </div>
                <div className="ml-auto">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Competition</p>
                  <p className="font-data font-bold">{product.competition_density} sellers</p>
                </div>
              </div>
            </div>

            {/* Alpha Score */}
            <div className="w-full lg:w-auto flex-shrink-0">
              <AlphaScoreGauge score={product.alpha_score} size="large" />
            </div>
          </div>
        </div>

        {/* Beginner Action Box */}
        {beginnerMode && (
          <div className="glass-heavy p-6 border-l-4 border-primary" data-testid="beginner-action-box">
            <h3 className="font-heading text-xl font-bold uppercase mb-2">
              What Should You Do?
            </h3>
            {product.status === "EXPLOSIVE" && (
              <p className="text-muted-foreground">
                This product is showing strong viral signals. <span className="text-primary font-semibold">
                Test this product within 24-48 hours</span> to capture the momentum. 
                Start with a small test order and prepare your content using the hooks below.
              </p>
            )}
            {product.status === "RISING" && (
              <p className="text-muted-foreground">
                This product is gaining traction steadily. <span className="text-primary font-semibold">
                Build your position over the next 1-2 weeks</span>. 
                Research suppliers, create sample content, and monitor for acceleration signals.
              </p>
            )}
            {product.status === "EARLY_SIGNAL" && (
              <p className="text-muted-foreground">
                Early accumulation detected but not yet viral. <span className="text-accent font-semibold">
                Add to your watchlist</span> and check back in 3-5 days. 
                If creator count increases significantly, consider testing.
              </p>
            )}
            {product.status === "WATCHLIST" && (
              <p className="text-muted-foreground">
                Mixed signals - not recommended for immediate action. 
                <span className="status-watchlist font-semibold"> Monitor weekly</span> for any changes in momentum.
              </p>
            )}
            {product.status === "AVOID" && (
              <p className="text-muted-foreground">
                Market appears saturated or declining. <span className="status-avoid font-semibold">
                Avoid this product</span> and focus your resources on better opportunities above.
              </p>
            )}
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-6">
            {/* Score Breakdown */}
            <ScoreBreakdown breakdown={product.score_breakdown} />

            {/* Trend Chart */}
            <TrendChart data={product.trend_data} />

            {/* Hook Analysis */}
            <HookAnalysis hooks={product.hook_analysis} />
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Market Validation */}
            <MarketValidation data={product.market_validation} />

            {/* Top Videos */}
            <TopVideos videos={product.top_videos} />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ProductDetail;
