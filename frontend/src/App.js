import React, { useState, useEffect, createContext, useContext } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useParams, useLocation, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import ProductDetail from "./pages/ProductDetail";
import Discover from "./pages/Discover";
import Alerts from "./pages/Alerts";
import Pricing from "./pages/Pricing";
import Watchlist from "./pages/Watchlist";
import Login from "./pages/Login";
import HookIntelligence from "./pages/HookIntelligence";
import MarketInsights from "./pages/MarketInsights";
import Admin from "./pages/Admin";
import Affiliates from "./pages/Affiliates";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import CommandBar from "./components/CommandBar";
import AuthCallback from "./components/AuthCallback";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for global state
export const AppContext = createContext();

export const useApp = () => useContext(AppContext);

// API Service — protected calls include withCredentials for cookie-based auth
export const api = {
  // Protected data endpoints
  getDashboardProducts: () => axios.get(`${API}/products/dashboard`, { withCredentials: true }),
  getProducts: (params) => axios.get(`${API}/products`, { params, withCredentials: true }),
  getProduct: (id) => axios.get(`${API}/products/${id}`, { withCredentials: true }),
  getStats: () => axios.get(`${API}/stats`, { withCredentials: true }),
  getAlerts: () => axios.get(`${API}/alerts`, { withCredentials: true }),
  markAlertRead: (id) => axios.post(`${API}/alerts/${id}/read`, {}, { withCredentials: true }),
  getCategories: () => axios.get(`${API}/categories`, { withCredentials: true }),
  refreshProducts: () => axios.post(`${API}/products/refresh`, {}, { withCredentials: true }),
  getDataStatus: () => axios.get(`${API}/data-status`, { withCredentials: true }),
  getTicker: () => axios.get(`${API}/ticker`, { withCredentials: true }),
  loadRealData: () => axios.post(`${API}/products/load-real-data`, {}, { withCredentials: true }),
  // Hook Intelligence & Market Validation
  getHookIntelligence: () => axios.get(`${API}/hooks/intelligence`, { withCredentials: true }),
  getMarketValidation: () => axios.get(`${API}/market/validation`, { withCredentials: true }),
  // AI Tools
  generateScripts: (productId) => axios.post(`${API}/ai/generate-scripts?product_id=${productId}`, {}, { withCredentials: true }),
  analyzeSentiment: (productId) => axios.post(`${API}/ai/analyze-sentiment?product_id=${productId}`, {}, { withCredentials: true }),
  getCachedScripts: (productId) => axios.get(`${API}/ai/scripts/${productId}`, { withCredentials: true }),
  getCachedSentiment: (productId) => axios.get(`${API}/ai/sentiment/${productId}`, { withCredentials: true }),
  // Ad Library
  getAdLibrary: (params) => axios.get(`${API}/ads`, { params, withCredentials: true }),
  getTopHooks: () => axios.get(`${API}/ads/top-hooks`, { withCredentials: true }),
  getDuplicationAlerts: () => axios.get(`${API}/ads/duplication-alerts`, { withCredentials: true }),
  // Forecast
  getProductForecast: (productId, days) => axios.get(`${API}/forecast/product/${productId}?days=${days || 14}`, { withCredentials: true }),
  getTopForecasts: () => axios.get(`${API}/forecast/top-forecasts`, { withCredentials: true }),
  // Store Tracking
  getTrackedStores: () => axios.get(`${API}/stores`, { withCredentials: true }),
  addStore: (storeUrl, name) => axios.post(`${API}/stores/add`, { store_url: storeUrl, name }, { withCredentials: true }),
  removeStore: (storeId) => axios.delete(`${API}/stores/${storeId}`, { withCredentials: true }),
  getStoreDetail: (storeId) => axios.get(`${API}/stores/${storeId}`, { withCredentials: true }),
  // Creator Marketplace
  getMarketplaceBriefs: (params) => axios.get(`${API}/marketplace/briefs`, { params, withCredentials: true }),
  createBrief: (data) => axios.post(`${API}/marketplace/briefs`, data, { withCredentials: true }),
  getBriefDetail: (id) => axios.get(`${API}/marketplace/briefs/${id}`, { withCredentials: true }),
  applyToBrief: (data) => axios.post(`${API}/marketplace/apply`, data, { withCredentials: true }),
  getMyBriefs: () => axios.get(`${API}/marketplace/my-briefs`, { withCredentials: true }),
  getMyApplications: () => axios.get(`${API}/marketplace/my-applications`, { withCredentials: true }),
  getMarketplaceStats: () => axios.get(`${API}/marketplace/stats`, { withCredentials: true }),
  // Public — subscription/checkout
  getPlans: () => axios.get(`${API}/plans`),
  createCheckout: (planId, email) => axios.post(`${API}/checkout/create?plan_id=${planId}${email ? `&user_email=${email}` : ''}`),
  getCheckoutStatus: (sessionId) => axios.get(`${API}/checkout/status/${sessionId}`),
  // Protected — watchlist
  getWatchlist: (userId) => axios.get(`${API}/watchlist/${userId}`, { withCredentials: true }),
  addToWatchlist: (userId, productId, notes) => axios.post(`${API}/watchlist/add?user_id=${userId}&product_id=${productId}${notes ? `&notes=${notes}` : ''}`, {}, { withCredentials: true }),
  removeFromWatchlist: (userId, productId) => axios.delete(`${API}/watchlist/remove?user_id=${userId}&product_id=${productId}`, { withCredentials: true }),
  // Auth APIs
  exchangeSession: (sessionId) => axios.post(`${API}/auth/session?session_id=${sessionId}`, {}, { withCredentials: true }),
  getMe: () => axios.get(`${API}/auth/me`, { withCredentials: true }),
  logout: () => axios.post(`${API}/auth/logout`, {}, { withCredentials: true }),
  updateSettings: (settings) => axios.put(`${API}/auth/settings`, null, { params: settings, withCredentials: true }),
  sendTestNotification: () => axios.post(`${API}/notifications/test`, {}, { withCredentials: true }),
  // Public — beta
  betaSignup: (email, name) => axios.post(`${API}/beta/signup?email=${email}${name ? `&name=${name}` : ''}`),
  getBetaStats: () => axios.get(`${API}/beta/stats`),
  // Subscription check
  checkSubscription: (email) => axios.get(`${API}/subscription/check?email=${email}`, { withCredentials: true }),
  // CSV exports
  exportProductsCsv: () => `${API}/export/products`,
  exportWatchlistCsv: (userId) => `${API}/export/watchlist/${userId}`,
  // Admin APIs
  adminLogin: (email, password) => axios.post(`${API}/admin/login`, { email, password }, { withCredentials: true }),
  adminMe: () => axios.get(`${API}/admin/me`, { withCredentials: true }),
  adminLogout: () => axios.post(`${API}/admin/logout`, {}, { withCredentials: true }),
  adminDashboard: () => axios.get(`${API}/admin/dashboard`, { withCredentials: true }),
  adminSubscribers: () => axios.get(`${API}/admin/subscribers`, { withCredentials: true }),
  adminUsers: () => axios.get(`${API}/admin/users`, { withCredentials: true }),
  adminPayments: () => axios.get(`${API}/admin/payments`, { withCredentials: true }),
  adminActivateSub: (email, planId) => axios.post(`${API}/admin/subscribers/${email}/activate?plan_id=${planId}`, {}, { withCredentials: true }),
  adminDeactivateSub: (email) => axios.post(`${API}/admin/subscribers/${email}/deactivate`, {}, { withCredentials: true }),
};

// Get or create user ID for watchlist
export const getUserId = () => {
  let userId = localStorage.getItem("alpha_user_id");
  if (!userId) {
    userId = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("alpha_user_id", userId);
  }
  return userId;
};

// Protected Route component
const ProtectedRoute = ({ children, user, subscription }) => {
  const navigate = useNavigate();
  
  // Check if user is authenticated and has active subscription
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (!subscription || subscription.status !== "active") {
    return <Navigate to="/pricing" replace />;
  }
  
  return children;
};

// Auth handler component
const AuthHandler = ({ children, setUser, setSubscription }) => {
  const location = useLocation();
  
  useEffect(() => {
    // Check for session_id in URL hash (OAuth callback)
    const hash = window.location.hash;
    if (hash && hash.includes("session_id")) {
      const params = new URLSearchParams(hash.replace("#", ""));
      const sessionId = params.get("session_id");
      
      if (sessionId) {
        api.exchangeSession(sessionId)
          .then((response) => {
            if (response.data.user) {
              setUser(response.data.user);
              localStorage.setItem("alpha_user", JSON.stringify(response.data.user));
              // Clear the hash
              window.history.replaceState(null, "", window.location.pathname);
              toast.success(`Welcome back, ${response.data.user.name}!`);
            }
          })
          .catch((error) => {
            console.error("Auth error:", error);
          });
      }
    }
  }, [location, setUser]);
  
  return children;
};

function App() {
  const [beginnerMode, setBeginnerMode] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [unreadAlerts, setUnreadAlerts] = useState(0);
  const [watchlistCount, setWatchlistCount] = useState(0);
  const [user, setUser] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load alerts
    loadAlerts();
    loadWatchlistCount();
    loadUser();
    
    // Check for saved beginner mode preference
    const saved = localStorage.getItem("beginnerMode");
    if (saved) setBeginnerMode(JSON.parse(saved));
  }, []);

  const loadUser = async () => {
    setIsLoading(true);
    
    // Try to get user from localStorage first
    const savedUser = localStorage.getItem("alpha_user");
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        // Check subscription
        await checkUserSubscription(parsedUser.email);
      } catch (e) {
        localStorage.removeItem("alpha_user");
      }
    }
    
    // Verify with server
    try {
      const res = await api.getMe();
      setUser(res.data);
      localStorage.setItem("alpha_user", JSON.stringify(res.data));
      await checkUserSubscription(res.data.email);
    } catch (e) {
      // Not authenticated - that's ok
    } finally {
      setIsLoading(false);
    }
  };

  const checkUserSubscription = async (email) => {
    try {
      const res = await api.checkSubscription(email);
      setSubscription(res.data);
      localStorage.setItem("alpha_subscription", JSON.stringify(res.data));
    } catch (e) {
      setSubscription(null);
      localStorage.removeItem("alpha_subscription");
    }
  };

  const loadAlerts = async () => {
    try {
      const res = await api.getAlerts();
      setAlerts(res.data);
      setUnreadAlerts(res.data.filter((a) => !a.read).length);
    } catch (e) {
      console.error("Failed to load alerts:", e);
    }
  };

  const loadWatchlistCount = async () => {
    try {
      const res = await api.getWatchlist(getUserId());
      setWatchlistCount(res.data.watchlist.length);
    } catch (e) {
      console.error("Failed to load watchlist:", e);
    }
  };

  const toggleBeginnerMode = () => {
    const newValue = !beginnerMode;
    setBeginnerMode(newValue);
    localStorage.setItem("beginnerMode", JSON.stringify(newValue));
    toast.success(newValue ? "Beginner Mode ON" : "Beginner Mode OFF");
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      setUser(null);
      setSubscription(null);
      localStorage.removeItem("alpha_user");
      localStorage.removeItem("alpha_subscription");
      toast.success("Logged out successfully");
    } catch (e) {
      console.error("Logout error:", e);
    }
  };

  // Check if user has active subscription
  const hasAccess = user && subscription && subscription.status === "active";

  return (
    <AppContext.Provider
      value={{
        beginnerMode,
        toggleBeginnerMode,
        alerts,
        unreadAlerts,
        loadAlerts,
        setAlerts,
        watchlistCount,
        setWatchlistCount,
        loadWatchlistCount,
        user,
        setUser,
        subscription,
        setSubscription,
        hasAccess,
        handleLogout,
        checkUserSubscription,
      }}
    >
      <div className="min-h-screen bg-background">
        <div className="noise-overlay" />
        <BrowserRouter>
          <CommandBar />
          <AuthHandler setUser={setUser} setSubscription={setSubscription}>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={hasAccess ? <Dashboard /> : <Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/auth/callback" element={<AuthCallback />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
              
              {/* Protected routes - require subscription */}
              <Route path="/discover" element={
                hasAccess ? <Discover /> : <Navigate to="/pricing" replace />
              } />
              <Route path="/alerts" element={
                hasAccess ? <Alerts /> : <Navigate to="/pricing" replace />
              } />
              <Route path="/watchlist" element={
                hasAccess ? <Watchlist /> : <Navigate to="/pricing" replace />
              } />
              <Route path="/hooks" element={
                hasAccess ? <HookIntelligence /> : <Navigate to="/pricing" replace />
              } />
              <Route path="/market" element={
                hasAccess ? <MarketInsights /> : <Navigate to="/pricing" replace />
              } />
              <Route path="/affiliates" element={
                hasAccess ? <Affiliates /> : <Navigate to="/pricing" replace />
              } />
              <Route path="/product/:id" element={
                hasAccess ? <ProductDetail /> : <Navigate to="/pricing" replace />
              } />
            </Routes>
          </AuthHandler>
        </BrowserRouter>
        <Toaster 
          position="bottom-right" 
          theme="dark"
          toastOptions={{
            style: {
              background: 'hsl(0 0% 6%)',
              border: '1px solid hsl(0 0% 13%)',
              color: 'white',
            },
          }}
        />
      </div>
    </AppContext.Provider>
  );
}

export default App;
