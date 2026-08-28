import { Stack } from 'expo-router';
import { ApolloProvider } from '@apollo/client';
import { apollo } from '../lib/apollo';

export default function RootLayout() {
  return (
    <ApolloProvider client={apollo}>
      <Stack screenOptions={{ headerShown: true }}>
        <Stack.Screen name="index" options={{ title: 'Login' }} />
        <Stack.Screen name="dashboard" options={{ title: 'Dashboard' }} />
      </Stack>
    </ApolloProvider>
  );
}
