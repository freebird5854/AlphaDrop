import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import { Skeleton } from "../components/ui/skeleton";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Bell,
  Flame,
  Zap,
  Gem,
  Check,
  ExternalLink,
} from "lucide-react";
import { toast } from "sonner";

const Alerts = () => {
  const navigate = useNavigate();
  const { beginnerMode, alerts, setAlerts, loadAlerts } = useApp();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    await loadAlerts();
    setLoading(false);
  };

  const handleMarkRead = async (alertId) => {
    try {
      await api.markAlertRead(alertId);
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, read: true } : a));
      toast.success("Alert marked as read");
    } catch (e) {
      toast.error("Failed to mark alert as read");
    }
  };

  const getAlertIcon = (type) => {
    const icons = {
      NEW_EXPLOSIVE: <Flame className="w-5 h-5" />,
      VELOCITY_SPIKE: <Zap className="w-5 h-5" />,
      LOW_COMPETITION_HIGH_DEMAND: <Gem className="w-5 h-5" />,
    };
    return icons[type] || <Bell className="w-5 h-5" />;
  };

  const getAlertColor = (severity) => {
    const colors = {
      critical: "border-l-status-explosive bg-status-explosive/5",
      warning: "border-l-status-rising bg-status-rising/5",
      info: "border-l-status-early bg-status-early/5",
    };
    return colors[severity] || "border-l-border";
  };

  const getSeverityBadge = (severity) => {
    const badges = {
      critical: "bg-status-explosive text-black",
      warning: "bg-status-rising text-black",
      info: "bg-status-early text-black",
    };
    return badges[severity] || "bg-muted";
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="alerts-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-4xl font-black tracking-tighter uppercase">
              <span className="text-primary">Alert</span> Center
            </h1>
            {beginnerMode && (
              <p className="text-muted-foreground mt-2 max-w-xl">
                Real-time notifications when products enter explosive territory or show significant changes.
              </p>
            )}
          </div>
          <Badge variant="outline" className="font-data">
            {alerts.filter(a => !a.read).length} unread
          </Badge>
        </div>

        {/* Alerts List */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-24 bg-card" />
            ))}
          </div>
        ) : alerts.length === 0 ? (
          <div className="glass p-12 text-center">
            <Bell className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-heading text-xl font-bold uppercase mb-2">No Alerts Yet</h3>
            <p className="text-muted-foreground">
              You'll be notified when products show significant changes
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div
                key={alert.id}
                className={`glass border-l-4 ${getAlertColor(alert.severity)} p-4 lg:p-6 transition-all animate-slide-up opacity-0 ${alert.read ? "opacity-60" : ""}`}
                style={{ animationDelay: `${index * 0.05}s` }}
                data-testid={`alert-item-${alert.id}`}
              >
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  {/* Icon & Content */}
                  <div className="flex items-start gap-4 flex-1">
                    <div className={`p-2 ${alert.read ? "bg-muted" : "bg-primary/10"} border border-border`}>
                      {getAlertIcon(alert.alert_type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`${getSeverityBadge(alert.severity)} font-data text-[10px] uppercase tracking-wider`}>
                          {alert.severity}
                        </Badge>
                        <span className="text-xs text-muted-foreground font-data">
                          {formatTime(alert.created_at)}
                        </span>
                      </div>
                      <p className="text-foreground font-medium">{alert.message}</p>
                      <p className="text-sm text-muted-foreground mt-1 font-data">
                        {alert.alert_type.replace(/_/g, " ")}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-12 lg:ml-0">
                    {!alert.read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMarkRead(alert.id)}
                        className="text-muted-foreground"
                        data-testid={`mark-read-${alert.id}`}
                      >
                        <Check className="w-4 h-4 mr-1" />
                        Mark Read
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/product/${alert.product_id}`)}
                      className="font-data"
                      data-testid={`view-product-${alert.id}`}
                    >
                      <ExternalLink className="w-4 h-4 mr-1" />
                      View
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Beginner Tip */}
        {beginnerMode && alerts.length > 0 && (
          <div className="glass-heavy p-6 border-l-4 border-accent" data-testid="beginner-tip">
            <h3 className="font-heading text-lg font-bold uppercase mb-2">
              Pro Tip
            </h3>
            <p className="text-muted-foreground text-sm">
              Critical alerts (marked in green) require immediate attention. 
              These are time-sensitive opportunities that may only last 24-48 hours. 
              Click "View" to see the full product analysis and decide if it's right for you.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Alerts;
