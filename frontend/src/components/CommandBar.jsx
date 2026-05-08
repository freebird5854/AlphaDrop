import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
} from "./ui/command";
import {
  LayoutDashboard, Compass, Target, Globe, Users, Bookmark,
  Bell, CreditCard, Search, Zap, TrendingUp, Flame,
} from "lucide-react";

const pages = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard, keywords: "home main overview" },
  { name: "Discover Products", path: "/discover", icon: Compass, keywords: "search find browse products" },
  { name: "Hook Intelligence", path: "/hooks", icon: Target, keywords: "hooks content angles scripts" },
  { name: "Market Validation", path: "/market", icon: Globe, keywords: "amazon google trends cross platform" },
  { name: "Affiliates", path: "/affiliates", icon: Users, keywords: "creators influencers niche" },
  { name: "Watchlist", path: "/watchlist", icon: Bookmark, keywords: "saved tracked favorites" },
  { name: "Alerts", path: "/alerts", icon: Bell, keywords: "notifications explosive" },
  { name: "Pricing", path: "/pricing", icon: CreditCard, keywords: "plans subscribe upgrade" },
];

const CommandBar = () => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const down = (e) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runAction = useCallback((path) => {
    setOpen(false);
    navigate(path);
  }, [navigate]);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search products, pages, actions..." data-testid="command-input" />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Pages">
          {pages.map((page) => (
            <CommandItem
              key={page.path}
              onSelect={() => runAction(page.path)}
              data-testid={`cmd-${page.name.toLowerCase().replace(/\s/g, "-")}`}
            >
              <page.icon className="mr-2 h-4 w-4 text-muted-foreground" />
              <span>{page.name}</span>
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Quick Actions">
          <CommandItem onSelect={() => runAction("/discover?status=EXPLOSIVE")}>
            <Flame className="mr-2 h-4 w-4 text-status-explosive" />
            <span>View Explosive Products</span>
          </CommandItem>
          <CommandItem onSelect={() => runAction("/discover?status=EXPLODING_SOON")}>
            <Zap className="mr-2 h-4 w-4 text-primary" />
            <span>View Exploding Soon</span>
          </CommandItem>
          <CommandItem onSelect={() => runAction("/discover?status=SATURATION_WARNING")}>
            <TrendingUp className="mr-2 h-4 w-4 text-status-avoid" />
            <span>View Saturation Warnings</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
};

export default CommandBar;
