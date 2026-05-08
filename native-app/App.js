import React from 'react';
import { SafeAreaView, StatusBar, Platform, View, ActivityIndicator, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';

// Replace with your production domain
const APP_URL = 'https://alphadrop.org';

export default function App() {
  const [loading, setLoading] = React.useState(true);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" translucent={false} />
      <WebView
        source={{ uri: APP_URL }}
        style={styles.webview}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        allowsBackForwardNavigationGestures={true}
        sharedCookiesEnabled={true}
        thirdPartyCookiesEnabled={true}
        mediaPlaybackRequiresUserAction={false}
        allowsInlineMediaPlayback={true}
        onLoadStart={() => setLoading(true)}
        onLoadEnd={() => setLoading(false)}
        renderLoading={() => (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#00FF94" />
          </View>
        )}
        // Handle external links
        onShouldStartLoadWithRequest={(request) => {
          if (request.url.includes('stripe.com') || request.url.includes('accounts.google.com')) {
            return true; // Allow payment & auth redirects
          }
          if (!request.url.includes('alphadrop')) {
            // Open external links in system browser
            return false;
          }
          return true;
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  webview: {
    flex: 1,
    backgroundColor: '#000',
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
});
