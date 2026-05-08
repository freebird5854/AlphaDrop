import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useApp } from "../App";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import { Badge } from "./ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  LayoutDashboard,
  Compass,
  Bell,
  HelpCircle,
  Menu,
  X,
  Zap,
  Bookmark,
  CreditCard,
  User,
  LogOut,
  Settings,
  Mail,
  Target,
  Globe,
  Users,
} from "lucide-react";

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { beginnerMode, toggleBeginnerMode, unreadAlerts, watchlistCount, user, handleLogout } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: "/", icon: LayoutDashboard, label: "Dashboard" },
    { path: "/discover", icon: Compass, label: "Discover" },
    { path: "/hooks", icon: Target, label: "Hooks" },
    { path: "/market", icon: Globe, label: "Market" },
    { path: "/affiliates", icon: Users, label: "Affiliates" },
    { path: "/watchlist", icon: Bookmark, label: "Watchlist", badge: watchlistCount },
    { path: "/alerts", icon: Bell, label: "Alerts", badge: unreadAlerts },
  ];

  const handleLogin = () => {
    navigate("/login");
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Navigation Bar - Command Center Style */}
      <header className="sticky top-0 z-50 glass-heavy border-b border-border" data-testid="header">
        <div className="max-w-[1800px] mx-auto px-4 lg:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div 
              className="flex items-center gap-3 cursor-pointer" 
              onClick={() => navigate("/")}
              data-testid="logo"
            >
              <div className="p-2 bg-primary">
                <Zap className="w-5 h-5 text-black" />
              </div>
              <div>
                <h1 className="font-heading text-xl font-black tracking-tighter uppercase leading-none">
                  Alpha<span className="text-primary">Drop</span>
                </h1>
                <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] leading-none">
                  Product Intelligence
                </p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-1">
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  variant={isActive(item.path) ? "secondary" : "ghost"}
                  onClick={() => navigate(item.path)}
                  className={`font-data text-xs uppercase tracking-wider relative ${
                    isActive(item.path) ? "text-primary" : ""
                  }`}
                  data-testid={`nav-${item.label.toLowerCase()}`}
                >
                  <item.icon className="w-4 h-4 mr-2" />
                  {item.label}
                  {item.badge > 0 && (
                    <Badge className="ml-2 bg-status-explosive text-black font-data text-[10px] px-1.5 py-0">
                      {item.badge}
                    </Badge>
                  )}
                </Button>
              ))}
            </nav>

            {/* Right Side Controls */}
            <div className="flex items-center gap-4">
              {/* Beginner Mode Toggle */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="hidden sm:flex items-center gap-2">
                      <HelpCircle className={`w-4 h-4 ${beginnerMode ? "text-primary" : "text-muted-foreground"}`} />
                      <span className="text-xs font-data uppercase tracking-wider text-muted-foreground">
                        Beginner
                      </span>
                      <Switch
                        checked={beginnerMode}
                        onCheckedChange={toggleBeginnerMode}
                        data-testid="beginner-mode-toggle"
                      />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">
                    <p>Toggle explanations and tips for new users</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {/* User Menu or Login Button */}
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="gap-2" data-testid="user-menu-btn">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-6 h-6 rounded-full" />
                      ) : (
                        <User className="w-4 h-4" />
                      )}
                      <span className="hidden md:inline text-xs font-data">{user.name?.split(' ')[0]}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <div className="px-2 py-1.5">
                      <p className="text-sm font-medium">{user.name}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => navigate("/watchlist")}>
                      <Bookmark className="w-4 h-4 mr-2" />
                      My Watchlist
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigate("/pricing")}>
                      <CreditCard className="w-4 h-4 mr-2" />
                      Subscription
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout} className="text-red-500">
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogin}
                  className="font-data text-xs uppercase"
                  data-testid="login-btn"
                >
                  <User className="w-4 h-4 mr-2" />
                  Login
                </Button>
              )}

              {/* Mobile Menu Toggle */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                data-testid="mobile-menu-toggle"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="lg:hidden py-4 border-t border-border animate-fade-in">
              <nav className="flex flex-col gap-2">
                {navItems.map((item) => (
                  <Button
                    key={item.path}
                    variant={isActive(item.path) ? "secondary" : "ghost"}
                    onClick={() => {
                      navigate(item.path);
                      setMobileMenuOpen(false);
                    }}
                    className={`justify-start font-data text-xs uppercase tracking-wider ${
                      isActive(item.path) ? "text-primary" : ""
                    }`}
                    data-testid={`mobile-nav-${item.label.toLowerCase()}`}
                  >
                    <item.icon className="w-4 h-4 mr-2" />
                    {item.label}
                    {item.badge > 0 && (
                      <Badge className="ml-auto bg-status-explosive text-black font-data text-[10px]">
                        {item.badge}
                      </Badge>
                    )}
                  </Button>
                ))}
                {/* Mobile Beginner Toggle */}
                <div className="flex items-center justify-between px-4 py-2 sm:hidden">
                  <div className="flex items-center gap-2">
                    <HelpCircle className={`w-4 h-4 ${beginnerMode ? "text-primary" : "text-muted-foreground"}`} />
                    <span className="text-xs font-data uppercase tracking-wider">Beginner Mode</span>
                  </div>
                  <Switch
                    checked={beginnerMode}
                    onCheckedChange={toggleBeginnerMode}
                    data-testid="mobile-beginner-mode-toggle"
                  />
                </div>
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-[1800px] w-full mx-auto px-4 lg:px-6 py-6 lg:py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 mt-auto" data-testid="footer">
        <div className="max-w-[1800px] mx-auto px-4 lg:px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-muted-foreground font-data uppercase tracking-wider">
              Alpha Drop © 2026 — Product Intelligence Engine
            </p>
            <p className="text-xs text-muted-foreground">
              Real-time TikTok Shop intelligence powered by AlphaDrop
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
