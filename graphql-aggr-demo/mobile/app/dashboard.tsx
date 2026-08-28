import { useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  Pressable,
} from 'react-native';
import { useQuery } from '@apollo/client';
import { useRouter } from 'expo-router';
import { DASHBOARD_QUERY } from '../lib/apollo';
import { clearTokens } from '../lib/auth';

export default function DashboardScreen() {
  const router = useRouter();
  const { data, loading, refetch } = useQuery(DASHBOARD_QUERY);

  const logout = useCallback(async () => {
    await clearTokens();
    router.replace('/');
  }, [router]);

  const orders = data?.dashboard?.orderInsights ?? [];
  const users = data?.dashboard?.activeUsers ?? [];

  return (
    <View style={styles.container}>
      <Pressable onPress={logout} style={styles.logout}>
        <Text style={styles.logoutText}>Logout</Text>
      </Pressable>

      <Text style={styles.section}>Orders (notification + inventory)</Text>
      <FlatList
        data={orders}
        keyExtractor={(item) => item.orderId}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={refetch} />}
        ListEmptyComponent={<Text style={styles.empty}>No orders yet</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.productName}</Text>
            <Text>Order: {item.orderId.slice(0, 8)}…</Text>
            <Text>Notification: {item.notificationStatus}</Text>
            <Text>Inventory left: {item.inventoryRemaining}</Text>
          </View>
        )}
        style={styles.list}
      />

      <Text style={styles.section}>Logged-in users (with DOB)</Text>
      <FlatList
        data={users}
        keyExtractor={(item) => item.userId}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.email}</Text>
            <Text>DOB: {item.dateOfBirth ?? '—'}</Text>
            <Text>Since: {new Date(item.loggedInAt).toLocaleString()}</Text>
          </View>
        )}
        style={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  section: { fontSize: 16, fontWeight: '600', margin: 12, marginBottom: 4 },
  list: { maxHeight: 220 },
  card: {
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginVertical: 6,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#eee',
  },
  cardTitle: { fontWeight: '600', marginBottom: 4 },
  empty: { textAlign: 'center', color: '#888', padding: 16 },
  logout: { alignSelf: 'flex-end', margin: 12 },
  logoutText: { color: '#2563eb' },
});
