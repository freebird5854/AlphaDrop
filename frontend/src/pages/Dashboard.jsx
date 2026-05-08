import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import ProductCard from "../components/ProductCard";
import StatsBar from "../components/StatsBar";
import AlphaScoreGauge from "../components/AlphaScoreGauge";
import { Skeleton } from "../components/ui/skeleton";
import { Button } from "../components/ui/button";
import { 
  Flame, 
  TrendingUp, 
  Eye, 
  RefreshCw,
  Zap,
  Target,
  ArrowRight,
  Database,
  Radio,
  Download,
  AlertTriangle,
  Rocket,
  Timer,
} from "lucide-react";
import { toast } from "sonner";

const Dashboard = () => {
  const navigate = useNavigate();
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingReal, setLoadingReal] = useState(false);
  const [dataStatus, setDataStatus] = useState(null);
  const [data, setData] = useState({
    explosive: [],
    exploding_soon: [],
    rising: [],
    early_signals: [],
    saturation_warnings: [],
  });
  const [stats, setStats] = useState(null);
  const [ticker, setTicker] = useState([]);

  useEffect(() => {
    loadData();
    checkDataStatus();
    loadTicker();
  }, []);

  const checkDataStatus = async () => {
    try {
      const res = await api.getDataStatus();
      setDataStatus(res.data);
    } catch (e) {
      console.error("Failed to check data status:", e);
    }
  };

  const loadTicker = async () => {
    try {
      const res = await api.getTicker();
      setTicker(res.data.ticker || []);
    } catch (e) {
      // Ticker is non-critical
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [dashRes, statsRes] = await Promise.all([
        api.getDashboardProducts(),
        api.getStats(),
      ]);
      setData(dashRes.data);
      setStats(statsRes.data);
    } catch (e) {
      console.error("Failed to load dashboard:", e);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await api.refreshProducts();
      await loadData();
      toast.success("Data refreshed with new products!");
    } catch (e) {
      toast.error("Failed to refresh data");
    } finally {
      setRefreshing(false);
    }
  };

  const handleLoadRealData = async () => {
    try {
      setLoadingReal(true);
      toast.info("Loading real TikTok Shop data... This may take 30-60 seconds.");
      const res = await api.loadRealData();
      await loadData();
      toast.success(`Loaded ${res.data.total_products} REAL products! ${res.data.explosive} Explosive, ${res.data.rising} Rising`);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to load real data");
    } finally {
      setLoadingReal(false);
    }
  };

  const SectionHeader = ({ icon: Icon, title, subtitle, color, count }) => (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        <div className={`p-3 ${color} bg-opacity-10 border border-current border-opacity-20`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h2 className="font-heading text-2xl font-bold tracking-tight uppercase flex items-center gap-3">
            {title}
            <span className="font-data text-sm font-normal text-muted-foreground">
              {count} PRODUCTS
            </span>
          </h2>
          {beginnerMode && (
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
      </div>
      <Button
        variant="outline"
        size="sm"
        className="font-data text-xs uppercase tracking-wider"
        onClick={() => navigate("/discover")}
        data-testid="view-all-btn"
      >
        View All <ArrowRight className="w-3 h-3 ml-2" />
      </Button>
    </div>
  );

  const ProductSection = ({ products, isLoading }) => {
    if (isLoading) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-64 bg-card" />
          ))}
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {products.map((product, index) => (
          <div
            key={product.id}
            className={`animate-slide-up opacity-0 stagger-${index + 1}`}
          >
            <ProductCard product={product} />
          </div>
        ))}
      </div>
    );
  };

  return (
    <Layout>
      <div className="space-y-8" data-testid="dashboard-page">
        {/* Hero Stats */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div>
            <h1 className="font-heading text-4xl md:text-5xl font-black tracking-tighter uppercase">
              <span className="text-primary">Alpha</span> Dashboard
            </h1>
            {beginnerMode && (
              <p className="text-muted-foreground mt-2 max-w-xl">
                This is your command center. Below are the best product opportunities 
                organized by their potential. Focus on "Explosive" products first.
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="font-data text-xs uppercase tracking-tight"
              onClick={() => {
                const url = api.exportProductsCsv();
                window.open(url, "_blank");
                toast.success("Downloading CSV...");
              }}
              data-testid="export-csv-btn"
            >
              <Download className="w-4 h-4 mr-2" /> Export CSV
            </Button>
            <Button
              onClick={handleRefresh}
              disabled={refreshing || loadingReal}
              variant="outline"
              className="font-data text-xs uppercase tracking-tight"
              data-testid="refresh-data-btn"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
              {refreshing ? "Refreshing..." : "Simulated"}
            </Button>
          </div>
          
          {dataStatus?.scrape_creators_configured && (
            <Button
              onClick={handleLoadRealData}
              disabled={loadingReal || refreshing}
              className="btn-skew bg-primary text-primary-foreground font-bold uppercase tracking-tight"
              data-testid="load-real-data-btn"
            >
              <span className="flex items-center gap-2">
                <Radio className={`w-4 h-4 ${loadingReal ? "animate-pulse" : ""}`} />
                {loadingReal ? "Loading Real Data..." : "Load REAL TikTok Data"}
              </span>
            </Button>
          )}
        </div>

        {/* Stats Bar */}
        <StatsBar stats={stats} loading={loading} />

        {/* Real-Time Ticker */}
        {ticker.length > 0 && (
          <div className="overflow-hidden border border-border bg-card/50 py-2" data-testid="ticker-bar">
            <div className="animate-marquee flex gap-8 whitespace-nowrap">
              {[...ticker, ...ticker].map((t, i) => (
                <span key={i} className="inline-flex items-center gap-2 text-xs font-data">
                  <span className={`w-2 h-2 rounded-full ${
                    t.status === "EXPLOSIVE" || t.status === "SCALING_NOW" ? "bg-status-explosive animate-pulse" :
                    t.status === "EXPLODING_SOON" ? "bg-primary animate-pulse" :
                    "bg-status-avoid"
                  }`} />
                  <span className="text-muted-foreground">{t.name?.substring(0, 25)}</span>
                  <span className={`font-bold ${
                    t.status === "SATURATION_WARNING" ? "text-status-avoid" : "text-primary"
                  }`}>{t.alpha_score}</span>
                  {t.momentum_multiplier > 1.1 && (
                    <span className="text-status-explosive text-[10px]">{t.momentum_multiplier}x</span>
                  )}
                  {t.saturation_countdown > 0 && t.saturation_countdown <= 14 && (
                    <span className="text-status-avoid text-[10px]">{t.saturation_countdown}d left</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Explosive Products */}
        <section data-testid="explosive-section">
          <SectionHeader
            icon={Flame}
            title="Explosive & Scaling"
            subtitle="These products are in active viral breakout. Consider entering within 24-48 hours."
            color="status-explosive"
            count={data.explosive.length}
          />
          <ProductSection products={data.explosive} isLoading={loading} />
        </section>

        {/* Exploding Soon */}
        {data.exploding_soon?.length > 0 && (
          <section data-testid="exploding-soon-section">
            <SectionHeader
              icon={Rocket}
              title="Exploding Soon"
              subtitle="Pre-viral accumulation phase. BEST risk/reward entry window right now."
              color="text-primary"
              count={data.exploding_soon.length}
            />
            <ProductSection products={data.exploding_soon} isLoading={loading} />
          </section>
        )}

        {/* Rising Products */}
        <section data-testid="rising-section">
          <SectionHeader
            icon={TrendingUp}
            title="Rising Fast"
            subtitle="Steady growth patterns detected. Good for building position over 1-2 weeks."
            color="status-rising"
            count={data.rising.length}
          />
          <ProductSection products={data.rising} isLoading={loading} />
        </section>

        {/* Early Signals */}
        <section data-testid="early-signals-section">
          <SectionHeader
            icon={Eye}
            title="Early Signals"
            subtitle="Pre-viral accumulation detected. Monitor these for the next big breakout."
            color="status-early"
            count={data.early_signals.length}
          />
          <ProductSection products={data.early_signals} isLoading={loading} />
        </section>

        {/* Saturation Warnings */}
        {data.saturation_warnings?.length > 0 && (
          <section data-testid="saturation-section">
            <SectionHeader
              icon={AlertTriangle}
              title="Saturation Warning"
              subtitle="These products are approaching market capacity. Exit or avoid new entry."
              color="text-status-avoid"
              count={data.saturation_warnings.length}
            />
            <ProductSection products={data.saturation_warnings} isLoading={loading} />
          </section>
        )}

        {/* Bottom CTA */}
        <div className="glass p-8 text-center">
          <h3 className="font-heading text-2xl font-bold uppercase mb-2">
            Want to discover more products?
          </h3>
          <p className="text-muted-foreground mb-6">
            Explore our full database with advanced filters and search
          </p>
          <Button
            onClick={() => navigate("/discover")}
            className="btn-skew bg-accent text-accent-foreground font-bold uppercase tracking-tight px-8"
            data-testid="explore-all-btn"
          >
            <span className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Explore All Products
            </span>
          </Button>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
