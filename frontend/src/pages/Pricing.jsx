import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api, useApp } from "../App";
import Layout from "../components/Layout";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Check,
  Zap,
  Target,
  Crown,
  ExternalLink,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";

const Pricing = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { beginnerMode } = useApp();
  const [plans, setPlans] = useState({});
  const [loading, setLoading] = useState(true);
  const [processingPlan, setProcessingPlan] = useState(null);
  const [email, setEmail] = useState("");

  useEffect(() => {
    loadPlans();
    
    // Check for payment status in URL
    const paymentStatus = searchParams.get("payment");
    const sessionId = searchParams.get("session_id");
    
    if (paymentStatus === "success" && sessionId) {
      checkPaymentStatus(sessionId);
    } else if (paymentStatus === "cancelled") {
      toast.error("Payment was cancelled");
    }
  }, [searchParams]);

  const loadPlans = async () => {
    try {
      const res = await api.getPlans();
      setPlans(res.data.plans);
    } catch (e) {
      toast.error("Failed to load plans");
    } finally {
      setLoading(false);
    }
  };

  const checkPaymentStatus = async (sessionId) => {
    try {
      const res = await api.getCheckoutStatus(sessionId);
      if (res.data.payment_status === "paid") {
        toast.success("Payment successful! Your subscription is now active.");
      }
    } catch (e) {
      console.error("Failed to check payment status:", e);
    }
  };

  const handleSubscribe = async (planId) => {
    if (!email) {
      toast.error("Please enter your email address");
      return;
    }
    
    try {
      setProcessingPlan(planId);
      const res = await api.createCheckout(planId, email);
      
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to create checkout");
    } finally {
      setProcessingPlan(null);
    }
  };

  const getPlanIcon = (planId) => {
    const icons = {
      scout: <Zap className="w-6 h-6" />,
      hunter: <Target className="w-6 h-6" />,
      predator: <Crown className="w-6 h-6" />,
      affiliate_pro: <Target className="w-6 h-6" />,
    };
    return icons[planId] || <Zap className="w-6 h-6" />;
  };

  const getPlanColor = (planId) => {
    const colors = {
      scout: "border-status-early",
      hunter: "border-status-rising",
      predator: "border-primary",
      affiliate_pro: "border-status-explosive",
    };
    return colors[planId] || "border-border";
  };

  // Separate main plans from add-ons
  const mainPlans = Object.entries(plans).filter(([, p]) => !p.is_addon);
  const addons = Object.entries(plans).filter(([, p]) => p.is_addon);

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-8" data-testid="pricing-page">
        {/* Header */}
        <div className="text-center">
          <h1 className="font-heading text-4xl md:text-5xl font-black tracking-tighter uppercase">
            <span className="text-primary">Upgrade</span> Your Edge
          </h1>
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            Get unlimited access to real TikTok Shop product intelligence. 
            Find winning products before they go viral.
          </p>
        </div>

        {/* Email Input */}
        <div className="max-w-md mx-auto">
          <label className="text-sm text-muted-foreground block mb-2">
            Enter your email to subscribe
          </label>
          <Input
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-card border-border font-data"
            data-testid="email-input"
          />
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {mainPlans.map(([planId, plan]) => (
            <div
              key={planId}
              className={`glass p-6 border-t-4 ${getPlanColor(planId)} relative ${
                planId === "hunter" ? "md:scale-105 md:-my-4" : ""
              }`}
              data-testid={`plan-${planId}`}
            >
              {planId === "hunter" && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-status-rising text-black font-data text-xs">
                  MOST POPULAR
                </Badge>
              )}

              <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 ${
                  planId === "predator" ? "bg-primary/10 text-primary" :
                  planId === "hunter" ? "bg-status-rising/10 text-status-rising" :
                  "bg-status-early/10 text-status-early"
                }`}>
                  {getPlanIcon(planId)}
                </div>
                <div>
                  <h3 className="font-heading text-xl font-bold uppercase">
                    {plan.name}
                  </h3>
                </div>
              </div>

              <div className="mb-6">
                <span className="font-data text-4xl font-bold">${plan.price}</span>
                <span className="text-muted-foreground">/month</span>
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Check className={`w-4 h-4 mt-0.5 ${
                      planId === "predator" ? "text-primary" :
                      planId === "hunter" ? "text-status-rising" :
                      "text-status-early"
                    }`} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                onClick={() => handleSubscribe(planId)}
                disabled={processingPlan === planId}
                className={`w-full font-data uppercase tracking-wider ${
                  planId === "predator" ? "bg-primary text-black hover:bg-primary/90" :
                  planId === "hunter" ? "bg-status-rising text-black hover:bg-status-rising/90" :
                  "bg-status-early text-black hover:bg-status-early/90"
                }`}
                data-testid={`subscribe-${planId}`}
              >
                {processingPlan === planId ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Subscribe <ExternalLink className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          ))}
        </div>

        {/* Add-ons */}
        {addons.length > 0 && (
          <div className="space-y-4">
            <h2 className="font-heading text-2xl font-bold uppercase tracking-tight text-center">
              Power <span className="text-status-explosive">Add-ons</span>
            </h2>
            <div className="grid md:grid-cols-1 max-w-xl mx-auto gap-4">
              {addons.map(([planId, plan]) => (
                <div
                  key={planId}
                  className="glass p-6 border-t-4 border-status-explosive"
                  data-testid={`plan-${planId}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-status-explosive/10 text-status-explosive">
                        {getPlanIcon(planId)}
                      </div>
                      <div>
                        <h3 className="font-heading text-xl font-bold uppercase">{plan.name}</h3>
                        <p className="text-xs text-muted-foreground font-data">
                          Requires Hunter plan &middot; Included in Predator
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="font-data text-3xl font-bold">+${plan.price}</span>
                      <span className="text-muted-foreground text-sm">/mo</span>
                    </div>
                  </div>
                  <ul className="grid grid-cols-2 gap-2 mb-6">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Check className="w-4 h-4 mt-0.5 text-status-explosive" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    onClick={() => handleSubscribe(planId)}
                    disabled={processingPlan === planId}
                    className="w-full bg-status-explosive text-black hover:bg-status-explosive/90 font-data uppercase tracking-wider"
                    data-testid={`subscribe-${planId}`}
                  >
                    {processingPlan === planId ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</>
                    ) : (
                      <>Add to Hunter Plan <ExternalLink className="w-4 h-4 ml-2" /></>
                    )}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* FAQ or Info */}
        {beginnerMode && (
          <div className="glass p-6 text-center">
            <h3 className="font-heading text-lg font-bold uppercase mb-2">
              Why Subscribe?
            </h3>
            <p className="text-muted-foreground text-sm max-w-2xl mx-auto">
              Free users get limited product views. Subscribers get full access to real-time 
              TikTok Shop data, unlimited product tracking, and the Alpha Score algorithm 
              that identifies winning products before they go viral. Most users make back 
              their subscription cost within the first week.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Pricing;
