# ALPHA DROP — Native App Store Deployment Guide

## Prerequisites
- Apple Developer Account ($99/yr) — https://developer.apple.com
- Google Play Console ($25 one-time) — https://play.google.com/console
- Node.js 18+ installed locally
- Expo CLI: `npm install -g expo-cli`

---

## Option A: Expo WebView Wrapper (Fastest — 1-2 days)

This wraps your existing web app in a native shell. No code rewrite needed.

### Step 1: Create Expo Project
```bash
npx create-expo-app AlphaDropApp --template blank
cd AlphaDropApp
npx expo install expo-web-browser react-native-webview
```

### Step 2: Replace App.js
```javascript
import { WebView } from 'react-native-webview';
import { SafeAreaView, StatusBar, Platform } from 'react-native';

export default function App() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#000' }}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      <WebView
        source={{ uri: 'https://YOUR_DOMAIN.com' }}
        style={{ flex: 1, backgroundColor: '#000' }}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        allowsBackForwardNavigationGestures={true}
        sharedCookiesEnabled={true}
      />
    </SafeAreaView>
  );
}
```

### Step 3: Configure app.json
```json
{
  "expo": {
    "name": "ALPHA DROP",
    "slug": "alpha-drop",
    "version": "1.0.0",
    "orientation": "default",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#000000"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.alphadrop.app",
      "buildNumber": "1"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#000000"
      },
      "package": "com.alphadrop.app",
      "versionCode": 1
    }
  }
}
```

### Step 4: Build for Stores
```bash
# Install EAS CLI
npm install -g eas-cli
eas login

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

---

## Option B: Capacitor Wrapper (Alternative)

If you prefer Capacitor over Expo:

```bash
npm install @capacitor/core @capacitor/cli
npx cap init "ALPHA DROP" "com.alphadrop.app"

# Build your React app
cd /app/frontend && yarn build

# Add platforms
npx cap add ios
npx cap add android

# Copy web build
npx cap copy

# Open in Xcode / Android Studio
npx cap open ios
npx cap open android
```

---

## App Store Assets Needed

### iOS (App Store Connect)
- App icon: 1024x1024 PNG (no alpha)
- Screenshots: 6.7" (1290x2796), 6.5" (1284x2778), 5.5" (1242x2208)
- App description, keywords, privacy policy URL
- App category: Business or Finance

### Android (Google Play Console)
- Hi-res icon: 512x512 PNG
- Feature graphic: 1024x500
- Screenshots: Phone (min 2), Tablet (min 1)
- Short description (80 chars), Full description (4000 chars)
- Content rating questionnaire
- Privacy policy URL

---

## App Store Description Template

**Title:** ALPHA DROP - TikTok Shop Intelligence

**Subtitle:** Find Viral Products Before They Blow Up

**Description:**
ALPHA DROP is the ultimate product intelligence engine for TikTok Shop. Our proprietary Alpha Score algorithm analyzes 7 key factors to identify products in the "accumulation phase" — before they go viral.

Features:
• Real-time TikTok Shop product tracking (271+ products)
• Proprietary 0-100 Alpha Score predicting viral potential
• Hook Intelligence — discover winning content angles
• Cross-Platform Market Validation (TikTok × Amazon × Google)
• Affiliate Marketplace — connect with niche creators
• Real-time alerts for explosive opportunities
• CSV exports and API access
• Team collaboration tools

Plans starting at $79/month.

**Keywords:** tiktok shop, product research, dropshipping, viral products, ecommerce, affiliate marketing, product intelligence

---

## Privacy Policy & Terms
You'll need these URLs before submitting. Create pages at:
- https://YOUR_DOMAIN.com/privacy
- https://YOUR_DOMAIN.com/terms

(I can help create these if needed)
