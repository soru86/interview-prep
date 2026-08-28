import {
  Injectable,
  Logger,
  OnModuleDestroy,
  OnModuleInit,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

interface ConsulServiceNode {
  Service: { Address: string; Port: number };
}

@Injectable()
export class ConsulRegistry implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(ConsulRegistry.name);
  private serviceId!: string;
  private readonly cache = new Map<string, { url: string; expires: number }>();
  private roundRobin = new Map<string, number>();
  private baseUrl!: string;

  constructor(private readonly config: ConfigService) {}

  private consulFetch(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${this.baseUrl}${path}`, init);
  }

  onModuleInit(): void {
    const host = this.config.get('CONSUL_HOST', 'localhost');
    const port = this.config.get('CONSUL_PORT', 8500);
    this.baseUrl = `http://${host}:${port}/v1`;

    const name = this.config.getOrThrow<string>('SERVICE_NAME');
    const servicePort = Number(this.config.getOrThrow('PORT'));
    const address = this.config.get('SERVICE_HOST', '127.0.0.1');
    const scheme = process.env.MTLS_ENABLED === 'false' ? 'http' : 'https';

    this.serviceId = `${name}-${process.pid}`;
    const checkUrl = `${scheme}://${address}:${servicePort}/health`;

    const body = {
      ID: this.serviceId,
      Name: name,
      Address: address,
      Port: servicePort,
      Check: {
        HTTP: checkUrl,
        Interval: '10s',
        Timeout: '5s',
        DeregisterCriticalServiceAfter: '1m',
      },
    };

    void this.consulFetch('/agent/service/register', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`status ${res.status}`);
        this.logger.log(`Registered ${name} at ${checkUrl}`);
      })
      .catch((err: Error) => this.logger.error(`Consul register failed: ${err.message}`));
  }

  async onModuleDestroy(): Promise<void> {
    if (this.serviceId) {
      try {
        await this.consulFetch(`/agent/service/deregister/${this.serviceId}`, {
          method: 'PUT',
        });
      } catch {
        /* ignore */
      }
    }
  }

  async resolve(serviceName: string): Promise<string> {
    const cached = this.cache.get(serviceName);
    if (cached && cached.expires > Date.now()) {
      return cached.url;
    }

    const res = await this.consulFetch(
      `/health/service/${serviceName}?passing=true`,
    );
    if (!res.ok) {
      throw new Error(`Consul lookup failed for ${serviceName}`);
    }

    const nodes = (await res.json()) as ConsulServiceNode[];
    if (!nodes?.length) {
      throw new Error(`No healthy instances for ${serviceName}`);
    }

    const idx = this.roundRobin.get(serviceName) ?? 0;
    const node = nodes[idx % nodes.length];
    this.roundRobin.set(serviceName, idx + 1);

    const scheme = process.env.MTLS_ENABLED === 'false' ? 'http' : 'https';
    const url = `${scheme}://${node.Service.Address}:${node.Service.Port}`;
    this.cache.set(serviceName, { url, expires: Date.now() + 30_000 });
    return url;
  }
}
