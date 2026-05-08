import React, { useState, useEffect } from "react";
import { api } from "../App";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  Zap, Users, CreditCard, BarChart3, Lock, LogOut, ShieldCheck,
  TrendingUp, Eye, Flame, Mail, Download, UserPlus, UserMinus,
} from "lucide-react";
import { toast } from "sonner";

const Admin = () => {
  const [authed, setAuthed] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [tab, setTab] = useState("overview");
  const [subscribers, setSubscribers] = useState([]);
  const [users, setUsers] = useState([]);
  const [payments, setPayments] = useState([]);
  const [grantEmail, setGrantEmail] = useState("");
  const [grantPlan, setGrantPlan] = useState("hunter");

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      await api.adminMe();
      setAuthed(true);
      loadDashboard();
    } catch {
      setAuthed(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.adminLogin(email, password);
      setAuthed(true);
      loadDashboard();
      toast.success("Admin access granted");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await api.adminLogout();
    setAuthed(false);
    setData(null);
    toast.success("Logged out");
  };

  const loadDashboard = async () => {
    try {
      const res = await api.adminDashboard();
      setData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadSubscribers = async () => {
    const res = await api.adminSubscribers();
    setSubscribers(res.data.subscribers);
  };

  const loadUsers = async () => {
    const res = await api.adminUsers();
    setUsers(res.data.users);
  };

  const loadPayments = async () => {
    const res = await api.adminPayments();
    setPayments(res.data.payments);
  };

  const handleTabChange = (t) => {
    setTab(t);
    if (t === "subscribers") loadSubscribers();
    if (t === "users") loadUsers();
    if (t === "payments") loadPayments();
  };

  const grantSubscription = async () => {
    if (!grantEmail) return toast.error("Enter an email");
    try {
      const res = await api.adminActivateSub(grantEmail, grantPlan);
      toast.success(res.data.message);
      setGrantEmail("");
      loadSubscribers();
      loadDashboard();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };

  const deactivateSub = async (userEmail) => {
    try {
      const res = await api.adminDeactivateSub(userEmail);
      toast.success(res.data.message);
      loadSubscribers();
      loadDashboard();
    } catch (err) {
      toast.error("Failed to deactivate");
    }
  };

  // Login screen
  if (!authed) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="noise-overlay" />
        <div className="glass p-8 w-full max-w-sm space-y-6" data-testid="admin-login">
          <div className="flex items-center gap-3 justify-center">
            <div className="p-2 bg-primary"><Zap className="w-5 h-5 text-black" /></div>
            <div>
              <h1 className="font-heading text-xl font-black tracking-tighter uppercase leading-none">
                Alpha<span className="text-primary">Drop</span>
              </h1>
              <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em]">Admin Panel</p>
            </div>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              type="email" placeholder="Admin email" value={email}
              onChange={(e) => setEmail(e.target.value)} className="bg-card border-border font-data"
              data-testid="admin-email-input"
            />
            <Input
              type="password" placeholder="Password" value={password}
              onChange={(e) => setPassword(e.target.value)} className="bg-card border-border font-data"
              data-testid="admin-password-input"
            />
            <Button type="submit" disabled={loading} className="w-full bg-primary text-black font-bold uppercase"
              data-testid="admin-login-btn">
              {loading ? "Authenticating..." : "Admin Login"}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "subscribers", label: "Subscribers", icon: CreditCard },
    { id: "users", label: "Users", icon: Users },
    { id: "payments", label: "Payments", icon: CreditCard },
  ];

  return (
    <div className="min-h-screen bg-background" data-testid="admin-dashboard">
      <div className="noise-overlay" />
      {/* Admin Header */}
      <header className="sticky top-0 z-50 glass-heavy border-b border-border">
        <div className="max-w-7xl mx-auto px-4 lg:px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-primary"><Zap className="w-4 h-4 text-black" /></div>
            <span className="font-heading text-lg font-black uppercase">Alpha<span className="text-primary">Drop</span></span>
            <Badge className="bg-status-explosive/10 text-status-explosive border-status-explosive/30 font-data text-[10px]">ADMIN</Badge>
          </div>
          <Button variant="ghost" size="sm" onClick={handleLogout} data-testid="admin-logout-btn">
            <LogOut className="w-4 h-4 mr-1" /> Logout
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 lg:px-6 py-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-1 border-b border-border pb-px">
          {tabs.map((t) => (
            <button key={t.id} onClick={() => handleTabChange(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 font-data text-xs uppercase tracking-wider border-b-2 -mb-px transition-colors ${
                tab === t.id ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
              }`} data-testid={`admin-tab-${t.id}`}>
              <t.icon className="w-3.5 h-3.5" /> {t.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {tab === "overview" && data && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Total Products", value: data.products.total, icon: BarChart3 },
                { label: "Explosive", value: data.products.explosive, icon: Flame, color: "text-status-explosive" },
                { label: "Active Subscribers", value: data.users.active_subscribers, icon: ShieldCheck, color: "text-primary" },
                { label: "Total Revenue", value: `$${data.revenue.total.toLocaleString()}`, icon: CreditCard, color: "text-status-rising" },
              ].map((stat) => (
                <div key={stat.label} className="glass p-4" data-testid={`admin-stat-${stat.label.toLowerCase().replace(/ /g, "-")}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <stat.icon className={`w-4 h-4 ${stat.color || "text-muted-foreground"}`} />
                    <span className="text-xs text-muted-foreground uppercase font-data">{stat.label}</span>
                  </div>
                  <p className={`font-data text-2xl font-bold ${stat.color || ""}`}>{stat.value}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Total Users", value: data.users.total, icon: Users },
                { label: "Beta Signups", value: data.beta_signups, icon: Mail },
                { label: "Rising", value: data.products.rising, icon: TrendingUp, color: "text-status-rising" },
                { label: "Early Signals", value: data.products.early_signal, icon: Eye, color: "text-status-early" },
              ].map((stat) => (
                <div key={stat.label} className="glass p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <stat.icon className={`w-4 h-4 ${stat.color || "text-muted-foreground"}`} />
                    <span className="text-xs text-muted-foreground uppercase font-data">{stat.label}</span>
                  </div>
                  <p className={`font-data text-2xl font-bold ${stat.color || ""}`}>{stat.value}</p>
                </div>
              ))}
            </div>

            {/* Grant subscription */}
            <div className="glass p-5 space-y-3">
              <h3 className="font-heading text-lg font-bold uppercase">Grant Subscription</h3>
              <div className="flex gap-3 items-end">
                <div className="flex-1">
                  <label className="text-xs text-muted-foreground font-data uppercase mb-1 block">User Email</label>
                  <Input value={grantEmail} onChange={(e) => setGrantEmail(e.target.value)}
                    placeholder="user@email.com" className="bg-card border-border font-data" data-testid="grant-email" />
                </div>
                <div className="w-40">
                  <label className="text-xs text-muted-foreground font-data uppercase mb-1 block">Plan</label>
                  <select value={grantPlan} onChange={(e) => setGrantPlan(e.target.value)}
                    className="w-full h-10 bg-card border border-border px-3 font-data text-sm" data-testid="grant-plan">
                    <option value="scout">Scout</option>
                    <option value="hunter">Hunter</option>
                    <option value="predator">Predator</option>
                  </select>
                </div>
                <Button onClick={grantSubscription} className="bg-primary text-black font-bold uppercase"
                  data-testid="grant-btn">
                  <UserPlus className="w-4 h-4 mr-1" /> Grant
                </Button>
              </div>
            </div>

            {/* Recent subs */}
            {data.recent_subscriptions?.length > 0 && (
              <div className="glass p-5">
                <h3 className="font-heading text-lg font-bold uppercase mb-3">Recent Subscriptions</h3>
                <div className="space-y-2">
                  {data.recent_subscriptions.map((sub, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-card border border-border">
                      <div>
                        <span className="text-sm">{sub.user_email}</span>
                        <Badge className="ml-2 font-data text-[10px]" variant="outline">{sub.plan_name}</Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={sub.status === "active" ? "bg-primary/10 text-primary" : "bg-status-avoid/10 text-status-avoid"}>
                          {sub.status}
                        </Badge>
                        <span className="text-xs text-muted-foreground font-data">{sub.started_at?.split("T")[0]}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Subscribers Tab */}
        {tab === "subscribers" && (
          <div className="glass p-5">
            <h3 className="font-heading text-lg font-bold uppercase mb-3">All Subscribers ({subscribers.length})</h3>
            <div className="space-y-2">
              {subscribers.map((sub, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-card border border-border">
                  <div>
                    <span className="text-sm">{sub.user_email}</span>
                    <Badge className="ml-2 font-data text-[10px]" variant="outline">{sub.plan_name}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={sub.status === "active" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}>
                      {sub.status}
                    </Badge>
                    {sub.status === "active" && (
                      <Button size="sm" variant="ghost" className="text-red-500 text-xs"
                        onClick={() => deactivateSub(sub.user_email)} data-testid={`deactivate-${i}`}>
                        <UserMinus className="w-3 h-3 mr-1" /> Deactivate
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              {subscribers.length === 0 && <p className="text-sm text-muted-foreground">No subscribers yet.</p>}
            </div>
          </div>
        )}

        {/* Users Tab */}
        {tab === "users" && (
          <div className="glass p-5">
            <h3 className="font-heading text-lg font-bold uppercase mb-3">All Users ({users.length})</h3>
            <div className="space-y-2">
              {users.map((user, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-card border border-border">
                  <div className="flex items-center gap-3">
                    {user.picture && <img src={user.picture} alt="" className="w-8 h-8 rounded-full" />}
                    <div>
                      <span className="text-sm font-medium">{user.name}</span>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground font-data">{user.created_at?.split("T")[0]}</span>
                </div>
              ))}
              {users.length === 0 && <p className="text-sm text-muted-foreground">No users yet.</p>}
            </div>
          </div>
        )}

        {/* Payments Tab */}
        {tab === "payments" && (
          <div className="glass p-5">
            <h3 className="font-heading text-lg font-bold uppercase mb-3">Payment Transactions ({payments.length})</h3>
            <div className="space-y-2">
              {payments.map((p, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-card border border-border">
                  <div>
                    <span className="text-sm">{p.user_email || "Anonymous"}</span>
                    <Badge className="ml-2 font-data text-[10px]" variant="outline">{p.plan_id}</Badge>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-data font-bold">${p.amount}</span>
                    <Badge className={p.payment_status === "paid" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}>
                      {p.payment_status}
                    </Badge>
                    <span className="text-xs text-muted-foreground font-data">{p.created_at?.split("T")[0]}</span>
                  </div>
                </div>
              ))}
              {payments.length === 0 && <p className="text-sm text-muted-foreground">No payments yet.</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
