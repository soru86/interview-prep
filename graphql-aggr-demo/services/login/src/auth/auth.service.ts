import { Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { InjectRepository } from '@nestjs/typeorm';
import { createHash, randomUUID } from 'crypto';
import { Repository } from 'typeorm';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { ConsulRegistry, createMtlsAgent, getServiceCertPaths, isMtlsEnabled } from '@graphql-aggr/service-mesh';
import { RefreshTokenEntity } from '../entities/refresh-token.entity';
import { SessionEntity } from '../entities/session.entity';
import { KafkaProducerService } from '../kafka/kafka-producer.service';

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresIn: string;
}

@Injectable()
export class AuthService {
  constructor(
    private readonly config: ConfigService,
    private readonly jwt: JwtService,
    private readonly http: HttpService,
    private readonly consul: ConsulRegistry,
    private readonly kafka: KafkaProducerService,
    @InjectRepository(SessionEntity)
    private readonly sessions: Repository<SessionEntity>,
    @InjectRepository(RefreshTokenEntity)
    private readonly refreshTokens: Repository<RefreshTokenEntity>,
  ) {}

  private hashRefresh(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private async verifyWithRegister(email: string, password: string): Promise<{ id: string; email: string }> {
    const base = await this.consul.resolve('register-service');
    const httpsAgent = isMtlsEnabled()
      ? createMtlsAgent(getServiceCertPaths('login-service'))
      : undefined;

    const { data } = await firstValueFrom(
      this.http.post<{ id: string; email: string }>(
        `${base}/internal/users/verify`,
        { email, password },
        { httpsAgent },
      ),
    );
    return data;
  }

  private signAccess(user: { id: string; email: string }): string {
    return this.jwt.sign(
      { sub: user.id, email: user.email, type: 'access' },
      {
        secret: this.config.getOrThrow('JWT_ACCESS_SECRET'),
        expiresIn: this.config.get('ACCESS_TOKEN_TTL', '15m'),
      },
    );
  }

  private async issueRefresh(userId: string): Promise<string> {
    const raw = randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    await this.refreshTokens.save(
      this.refreshTokens.create({
        userId,
        tokenHash: this.hashRefresh(raw),
        expiresAt,
        revokedAt: null,
      }),
    );
    return raw;
  }

  private async upsertSession(user: { id: string; email: string }): Promise<void> {
    const existing = await this.sessions.find({ where: { userId: user.id } });
    if (existing.length) {
      await this.sessions.remove(existing);
    }
    await this.sessions.save(
      this.sessions.create({
        userId: user.id,
        email: user.email,
        loggedInAt: new Date(),
        expiresAt: null,
      }),
    );
  }

  async login(email: string, password: string): Promise<TokenPair> {
    let user: { id: string; email: string };
    try {
      user = await this.verifyWithRegister(email, password);
    } catch {
      throw new UnauthorizedException('Invalid credentials');
    }

    const accessToken = this.signAccess(user);
    const refreshToken = await this.issueRefresh(user.id);
    await this.upsertSession(user);
    await this.kafka.emitLoggedIn({ userId: user.id, email: user.email });

    return {
      accessToken,
      refreshToken,
      expiresIn: this.config.get('ACCESS_TOKEN_TTL', '15m'),
    };
  }

  async refresh(refreshToken: string): Promise<TokenPair> {
    const hash = this.hashRefresh(refreshToken);
    const record = await this.refreshTokens.findOne({ where: { tokenHash: hash } });
    if (!record || record.revokedAt || record.expiresAt < new Date()) {
      throw new UnauthorizedException('Invalid refresh token');
    }

    record.revokedAt = new Date();
    await this.refreshTokens.save(record);

    const session = await this.sessions.findOne({ where: { userId: record.userId } });
    if (!session) {
      throw new UnauthorizedException('Session not found');
    }

    const user = { id: record.userId, email: session.email };
    const accessToken = this.signAccess(user);
    const newRefresh = await this.issueRefresh(user.id);

    return {
      accessToken,
      refreshToken: newRefresh,
      expiresIn: this.config.get('ACCESS_TOKEN_TTL', '15m'),
    };
  }

  async logout(refreshToken: string): Promise<void> {
    const hash = this.hashRefresh(refreshToken);
    const record = await this.refreshTokens.findOne({ where: { tokenHash: hash } });
    if (record) {
      record.revokedAt = new Date();
      await this.refreshTokens.save(record);
      const sessions = await this.sessions.find({ where: { userId: record.userId } });
      if (sessions.length) {
        await this.sessions.remove(sessions);
        await this.kafka.emitLoggedOut({ userId: record.userId, email: sessions[0].email });
      }
    }
  }

  listActiveSessions(): Promise<SessionEntity[]> {
    return this.sessions.find({ order: { loggedInAt: 'DESC' } });
  }
}
