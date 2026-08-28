import { Injectable, Logger } from '@nestjs/common';
import { BackendClientService } from '../clients/backend-client.service';

interface OrderRow {
  id: string;
  userId: string;
  productSku: string;
  quantity: number;
}

interface NotificationRow {
  orderId: string;
  status: 'PENDING' | 'SENT' | 'FAILED';
  detail: string | null;
}

interface ProductRow {
  sku: string;
  name: string;
  inventoryCount: number;
}

interface SessionRow {
  userId: string;
  email: string;
  loggedInAt: string;
}

interface ProfileRow {
  userId: string;
  email: string;
  dateOfBirth: string | null;
}

@Injectable()
export class DashboardService {
  private readonly logger = new Logger(DashboardService.name);

  constructor(private readonly backend: BackendClientService) {}

  async getDashboard() {
    const started = Date.now();

    const [orders, sessions] = await Promise.all([
      this.backend.get<OrderRow[]>('order-service', '/orders'),
      this.backend.get<SessionRow[]>('login-service', '/sessions/active'),
    ]);

    const orderIds = orders.map((o) => o.id);
    const skus = [...new Set(orders.map((o) => o.productSku))];
    const userIds = sessions.map((s) => s.userId);

    const [notifications, products, profiles] = await Promise.all([
      orderIds.length
        ? this.backend.get<NotificationRow[]>(
            'notification-service',
            `/attempts/by-order-ids?ids=${orderIds.join(',')}`,
          )
        : Promise.resolve([]),
      skus.length
        ? this.backend.get<ProductRow[]>(
            'catalog-service',
            `/products/by-skus?skus=${skus.join(',')}`,
          )
        : Promise.resolve([]),
      userIds.length
        ? this.backend.get<ProfileRow[]>(
            'profile-service',
            `/profiles?userIds=${userIds.join(',')}`,
          )
        : Promise.resolve([]),
    ]);

    const notificationByOrder = new Map(notifications.map((n) => [n.orderId, n]));
    const productBySku = new Map(products.map((p) => [p.sku, p]));
    const profileByUser = new Map(profiles.map((p) => [p.userId, p]));

    const orderInsights = orders
      .filter((o) => notificationByOrder.has(o.id))
      .map((o) => {
        const n = notificationByOrder.get(o.id)!;
        const p = productBySku.get(o.productSku);
        return {
          orderId: o.id,
          productSku: o.productSku,
          productName: p?.name ?? o.productSku,
          quantity: o.quantity,
          notificationStatus: n.status,
          notificationDetail: n.detail,
          inventoryRemaining: p?.inventoryCount ?? 0,
        };
      });

    const activeUsers = sessions.map((s) => {
      const profile = profileByUser.get(s.userId);
      return {
        userId: s.userId,
        email: s.email,
        loggedInAt: s.loggedInAt,
        dateOfBirth: profile?.dateOfBirth ?? null,
      };
    });

    this.logger.log(`Dashboard aggregated in ${Date.now() - started}ms`);

    return { orderInsights, activeUsers };
  }
}
