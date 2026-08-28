import { Injectable, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import {
  ConsulRegistry,
  createMtlsAgent,
  getServiceCertPaths,
  isMtlsEnabled,
} from '@graphql-aggr/service-mesh';

@Injectable()
export class BackendClientService {
  private readonly logger = new Logger(BackendClientService.name);
  private readonly agent = isMtlsEnabled()
    ? createMtlsAgent(getServiceCertPaths('gateway-client'))
    : undefined;

  constructor(
    private readonly http: HttpService,
    private readonly consul: ConsulRegistry,
  ) {}

  private fallbackUrl(serviceName: string): string {
    const scheme = process.env.MTLS_ENABLED === 'false' ? 'http' : 'https';
    const ports: Record<string, number> = {
      'register-service': 3001,
      'login-service': 3002,
      'profile-service': 3003,
      'order-service': 3004,
      'notification-service': 3005,
      'catalog-service': 3006,
    };
    const port = ports[serviceName] ?? 3000;
    return `${scheme}://127.0.0.1:${port}`;
  }

  async get<T>(serviceName: string, path: string): Promise<T> {
    let base: string;
    try {
      base = await this.consul.resolve(serviceName);
    } catch {
      base = this.fallbackUrl(serviceName);
      this.logger.warn(`Consul unavailable, using fallback ${base}`);
    }
    const url = `${base}${path}`;
    const started = Date.now();
    const { data } = await firstValueFrom(
      this.http.get<T>(url, {
        httpsAgent: this.agent,
        timeout: 5000,
      }),
    );
    this.logger.log(`GET ${url} (${Date.now() - started}ms)`);
    return data;
  }
}
