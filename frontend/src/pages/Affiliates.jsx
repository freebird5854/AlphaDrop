import React, { useState, useEffect } from "react";
import { useApp } from "../App";
import Layout from "../components/Layout";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";
import {
  Users, Search, Star, Mail, MessageCircle, TrendingUp,
  ShoppingCart, Filter, ChevronDown, ExternalLink,
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

const Affiliates = () => {
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedNiche, setSelectedNiche] = useState("");
  const [sortBy, setSortBy] = useState("followers");

  useEffect(() => { loadData(); }, [selectedNiche, sortBy]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ limit: "60", sort_by: sortBy });
      if (selectedNiche) params.append("niche", selectedNiche);
      if (search) params.append("search", search);
      const res = await axios.get(`${BACKEND}/api/affiliates?${params}`, { withCredentials: true });
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadData();
  };

  const fmtNum = (n) => {
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
    return String(n);
  };

  const engColor = (r) => {
    if (r >= 8) return "text-status-explosive";
    if (r >= 5) return "text-status-rising";
    return "text-status-early";
  };

  if (loading && !data) {
    return (
      <Layout>
        <div className="space-y-6" data-testid="affiliates-loading">
          <Skeleton className="h-20 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1,2,3,4,5,6].map(i => <Skeleton key={i} className="h-48" />)}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6" data-testid="affiliates-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-status-explosive/10 border border-status-explosive/30">
              <Users className="w-7 h-7 text-status-explosive" />
            </div>
            <div>
              <h1 className="font-heading text-3xl md:text-4xl font-black tracking-tighter uppercase leading-none">
                Affiliate <span className="text-status-explosive">Marketplace</span>
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                {data?.total || 0} creators across {data?.niches?.length || 0} niches
              </p>
            </div>
          </div>
          {beginnerMode && (
            <div className="glass p-3 max-w-sm border-l-2 border-status-explosive">
              <p className="text-xs text-muted-foreground">
                <span className="text-status-explosive font-bold">TIP:</span> Find creators in your product's
                niche and reach out for affiliate partnerships. Higher engagement rate = better ROI.
              </p>
            </div>
          )}
        </div>

        {/* Niche Stats */}
        {data?.niche_stats && (
          <div className="flex gap-2 overflow-x-auto pb-2">
            <button
              onClick={() => setSelectedNiche("")}
              className={`px-3 py-1.5 text-xs font-data uppercase tracking-wider whitespace-nowrap border transition-colors ${
                !selectedNiche ? "bg-primary text-black border-primary" : "border-border text-muted-foreground hover:text-foreground"
              }`}
              data-testid="niche-all"
            >All Niches</button>
            {data.niche_stats.map((n) => (
              <button
                key={n.niche}
                onClick={() => setSelectedNiche(n.niche)}
                className={`px-3 py-1.5 text-xs font-data uppercase tracking-wider whitespace-nowrap border transition-colors ${
                  selectedNiche === n.niche ? "bg-primary text-black border-primary" : "border-border text-muted-foreground hover:text-foreground"
                }`}
                data-testid={`niche-${n.niche.replace(/\s/g, "-").toLowerCase()}`}
              >{n.niche} ({n.count})</button>
            ))}
          </div>
        )}

        {/* Search + Sort */}
        <div className="flex gap-3">
          <form onSubmit={handleSearch} className="flex-1 flex gap-2">
            <Input
              value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Search creators..." className="bg-card border-border font-data"
              data-testid="affiliate-search"
            />
            <Button type="submit" variant="outline" size="sm"><Search className="w-4 h-4" /></Button>
          </form>
          <select
            value={sortBy} onChange={(e) => setSortBy(e.target.value)}
            className="h-10 bg-card border border-border px-3 font-data text-xs uppercase"
            data-testid="affiliate-sort"
          >
            <option value="followers">Followers</option>
            <option value="engagement_rate">Engagement</option>
            <option value="avg_commission">Commission</option>
            <option value="rating">Rating</option>
          </select>
        </div>

        {/* Creator Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data?.affiliates || []).map((a, idx) => (
            <div key={a.id} className="glass p-4 space-y-3 hover:border-primary/30 transition-colors" data-testid={`affiliate-${idx}`}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-heading text-base font-bold uppercase tracking-tight">{a.handle}</h3>
                  <p className="text-xs text-muted-foreground">{a.name}</p>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-status-rising" />
                  <span className="font-data text-xs font-bold">{a.rating}</span>
                </div>
              </div>

              <div className="flex gap-1 flex-wrap">
                <Badge className="bg-primary/10 text-primary border-primary/30 text-[9px] font-data">{a.niche}</Badge>
                {a.secondary_niche && (
                  <Badge variant="outline" className="text-[9px] font-data">{a.secondary_niche}</Badge>
                )}
                <Badge className={`text-[9px] font-data ${
                  a.status === "Active" ? "bg-status-rising/10 text-status-rising border-status-rising/30" :
                  a.status === "Selective" ? "bg-status-early/10 text-status-early border-status-early/30" :
                  "bg-status-explosive/10 text-status-explosive border-status-explosive/30"
                }`} variant="outline">{a.status}</Badge>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div className="text-center p-2 bg-card border border-border">
                  <p className="font-data text-sm font-bold">{fmtNum(a.followers)}</p>
                  <p className="text-[9px] text-muted-foreground uppercase">Followers</p>
                </div>
                <div className="text-center p-2 bg-card border border-border">
                  <p className={`font-data text-sm font-bold ${engColor(a.engagement_rate)}`}>{a.engagement_rate}%</p>
                  <p className="text-[9px] text-muted-foreground uppercase">Engagement</p>
                </div>
                <div className="text-center p-2 bg-card border border-border">
                  <p className="font-data text-sm font-bold text-primary">{a.avg_commission}%</p>
                  <p className="text-[9px] text-muted-foreground uppercase">Avg Comm.</p>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{a.products_promoted} products promoted</span>
                <span>{fmtNum(a.total_sales_driven)} sales driven</span>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-border">
                <div className="flex items-center gap-1 text-xs">
                  {a.contact_method === "Email" ? <Mail className="w-3 h-3" /> : <MessageCircle className="w-3 h-3" />}
                  <span className="text-muted-foreground">{a.contact_method}</span>
                </div>
                <Button
                  size="sm" variant="outline" className="text-xs font-data h-7"
                  onClick={() => {
                    navigator.clipboard.writeText(a.contact_email);
                    toast.success(`Copied: ${a.contact_email}`);
                  }}
                  data-testid={`copy-contact-${idx}`}
                >
                  <Mail className="w-3 h-3 mr-1" /> Copy Contact
                </Button>
              </div>

              {a.agency && (
                <div className="text-[10px] text-muted-foreground">
                  Agency: <span className="text-foreground">{a.agency}</span>
                </div>
              )}
            </div>
          ))}
        </div>
        {data?.affiliates?.length === 0 && (
          <p className="text-center text-muted-foreground py-12">No affiliates match your filters.</p>
        )}
      </div>
    </Layout>
  );
};

export default Affiliates;
