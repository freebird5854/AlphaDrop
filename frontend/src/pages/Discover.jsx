import React, { useState, useEffect, useCallback } from "react";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import ProductCard from "../components/ProductCard";
import { Skeleton } from "../components/ui/skeleton";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Slider } from "../components/ui/slider";
import { Badge } from "../components/ui/badge";
import {
  Search,
  Filter,
  X,
  SlidersHorizontal,
} from "lucide-react";
import { toast } from "sonner";

const Discover = () => {
  const { beginnerMode } = useApp();
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  // Filter state
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [category, setCategory] = useState("all");
  const [scoreRange, setScoreRange] = useState([0, 100]);

  useEffect(() => {
    loadCategories();
    loadProducts();
  }, []);

  const loadCategories = async () => {
    try {
      const res = await api.getCategories();
      setCategories(res.data.categories);
    } catch (e) {
      console.error("Failed to load categories:", e);
    }
  };

  const loadProducts = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        limit: 50,
      };
      if (search) params.search = search;
      if (status !== "all") params.status = status;
      if (category !== "all") params.category = category;
      if (scoreRange[0] > 0) params.min_score = scoreRange[0];
      if (scoreRange[1] < 100) params.max_score = scoreRange[1];

      const res = await api.getProducts(params);
      setProducts(res.data);
    } catch (e) {
      console.error("Failed to load products:", e);
      toast.error("Failed to load products");
    } finally {
      setLoading(false);
    }
  }, [search, status, category, scoreRange]);

  useEffect(() => {
    const debounce = setTimeout(() => {
      loadProducts();
    }, 300);
    return () => clearTimeout(debounce);
  }, [search, status, category, scoreRange, loadProducts]);

  const clearFilters = () => {
    setSearch("");
    setStatus("all");
    setCategory("all");
    setScoreRange([0, 100]);
  };

  const hasActiveFilters = search || status !== "all" || category !== "all" || scoreRange[0] > 0 || scoreRange[1] < 100;

  const statusOptions = [
    { value: "all", label: "All Status" },
    { value: "EXPLOSIVE", label: "Explosive" },
    { value: "RISING", label: "Rising" },
    { value: "EARLY_SIGNAL", label: "Early Signal" },
    { value: "WATCHLIST", label: "Watchlist" },
    { value: "AVOID", label: "Avoid" },
  ];

  return (
    <Layout>
      <div className="space-y-6" data-testid="discover-page">
        {/* Header */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <h1 className="font-heading text-4xl font-black tracking-tighter uppercase">
              <span className="text-accent">Discover</span> Products
            </h1>
            {beginnerMode && (
              <p className="text-muted-foreground mt-2">
                Browse and filter all tracked products. Use filters to find specific opportunities.
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="font-data">
              {products.length} products
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="lg:hidden"
              data-testid="toggle-filters-btn"
            >
              <SlidersHorizontal className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="glass p-4 lg:p-6 space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              placeholder="Search products or categories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-12 h-12 bg-card border-border font-data"
              data-testid="search-input"
            />
          </div>

          {/* Filter Row */}
          <div className={`${showFilters ? "block" : "hidden"} lg:block space-y-4 lg:space-y-0 lg:flex lg:items-center lg:gap-4`}>
            {/* Status Filter */}
            <div className="flex-1">
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger className="bg-card border-border font-data" data-testid="status-filter">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value} className="font-data">
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Category Filter */}
            <div className="flex-1">
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="bg-card border-border font-data" data-testid="category-filter">
                  <SelectValue placeholder="Filter by category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all" className="font-data">All Categories</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat} className="font-data">
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Score Range */}
            <div className="flex-1 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">
                  Alpha Score Range
                </span>
                <span className="font-data text-sm">
                  {scoreRange[0]} - {scoreRange[1]}
                </span>
              </div>
              <Slider
                value={scoreRange}
                onValueChange={setScoreRange}
                min={0}
                max={100}
                step={5}
                className="py-2"
                data-testid="score-range-slider"
              />
            </div>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="text-muted-foreground"
                data-testid="clear-filters-btn"
              >
                <X className="w-4 h-4 mr-1" />
                Clear
              </Button>
            )}
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-64 bg-card" />
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="glass p-12 text-center">
            <Filter className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-heading text-xl font-bold uppercase mb-2">No Products Found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your filters or search terms
            </p>
            <Button onClick={clearFilters} variant="outline" data-testid="clear-filters-empty-btn">
              Clear All Filters
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {products.map((product, index) => (
              <div
                key={product.id}
                className={`animate-slide-up opacity-0`}
                style={{ animationDelay: `${Math.min(index * 0.03, 0.3)}s` }}
              >
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Discover;
