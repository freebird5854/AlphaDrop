import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../App";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  Zap,
  Mail,
  ArrowRight,
  Check,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";

// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH

const Login = () => {
  const navigate = useNavigate();
  const [betaEmail, setBetaEmail] = useState("");
  const [betaName, setBetaName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSignedUp, setIsSignedUp] = useState(false);
  const [waitlistPosition, setWaitlistPosition] = useState(0);

  const handleGoogleLogin = () => {
    // CRITICAL: Use window.location.origin dynamically - no hardcoding!
    const redirectUrl = window.location.origin + '/';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleBetaSignup = async (e) => {
    e.preventDefault();
    if (!betaEmail) {
      toast.error("Please enter your email");
      return;
    }

    try {
      setIsSubmitting(true);
      const res = await api.betaSignup(betaEmail, betaName);
      
      if (res.data.status === "existing") {
        toast.info("You're already on the waitlist!");
      } else {
        setIsSignedUp(true);
        setWaitlistPosition(res.data.position);
        toast.success("Welcome to the beta!");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to sign up");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="noise-overlay" />
      
      {/* Header */}
      <header className="p-6">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate("/")}>
          <div className="p-2 bg-primary">
            <Zap className="w-5 h-5 text-black" />
          </div>
          <div>
            <h1 className="font-heading text-xl font-black tracking-tighter uppercase leading-none">
              Alpha<span className="text-primary">Drop</span>
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="glass p-8 space-y-6">
            {/* Title */}
            <div className="text-center">
              <Badge className="bg-primary/10 text-primary border-primary/20 mb-4">
                BETA ACCESS
              </Badge>
              <h2 className="font-heading text-3xl font-black tracking-tight uppercase">
                Get Early Access
              </h2>
              <p className="text-muted-foreground mt-2">
                Join 100 founding members and get 25% off for life
              </p>
            </div>

            {!isSignedUp ? (
              <>
                {/* Google Login */}
                <Button
                  onClick={handleGoogleLogin}
                  className="w-full h-12 bg-white hover:bg-gray-100 text-black font-medium"
                  data-testid="google-login-btn"
                >
                  <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border"></div>
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">Or join waitlist</span>
                  </div>
                </div>

                {/* Beta Signup Form */}
                <form onSubmit={handleBetaSignup} className="space-y-4">
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    value={betaEmail}
                    onChange={(e) => setBetaEmail(e.target.value)}
                    className="h-12 bg-card border-border"
                    data-testid="beta-email-input"
                  />
                  <Input
                    type="text"
                    placeholder="Your name (optional)"
                    value={betaName}
                    onChange={(e) => setBetaName(e.target.value)}
                    className="h-12 bg-card border-border"
                    data-testid="beta-name-input"
                  />
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full h-12 bg-primary text-black font-bold uppercase"
                    data-testid="beta-signup-btn"
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        Join Beta Waitlist <ArrowRight className="w-4 h-4 ml-2" />
                      </>
                    )}
                  </Button>
                </form>
              </>
            ) : (
              /* Success State */
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Check className="w-8 h-8 text-primary" />
                </div>
                <h3 className="font-heading text-xl font-bold uppercase mb-2">
                  You're In!
                </h3>
                <p className="text-muted-foreground mb-4">
                  You're #{waitlistPosition} on the waitlist. We'll email you when your spot opens up.
                </p>
                <div className="p-4 bg-card border border-border">
                  <p className="text-sm text-muted-foreground">
                    <span className="text-primary font-medium">Founding member perks:</span><br/>
                    14-day free trial • 25% off for life • Priority support
                  </p>
                </div>
              </div>
            )}

            {/* Features */}
            <div className="pt-4 border-t border-border">
              <p className="text-xs text-muted-foreground text-center mb-3">
                What you get with ALPHA DROP:
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  "Real TikTok Shop data",
                  "Alpha Score algorithm",
                  "Explosive alerts",
                  "Product watchlist"
                ].map((feature) => (
                  <div key={feature} className="flex items-center gap-2 text-muted-foreground">
                    <Check className="w-3 h-3 text-primary" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Already have access */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            Already have access?{" "}
            <button
              onClick={handleGoogleLogin}
              className="text-primary hover:underline"
            >
              Sign in
            </button>
          </p>
        </div>
      </main>
    </div>
  );
};

export default Login;
