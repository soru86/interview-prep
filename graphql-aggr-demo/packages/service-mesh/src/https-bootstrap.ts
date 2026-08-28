import { NestExpressApplication } from '@nestjs/platform-express';
import * as https from 'https';
import { readHttpsOptions, isMtlsEnabled, getServiceCertPaths, MtlsPaths } from './mtls';

export async function listenHttps(
  app: NestExpressApplication,
  port: number,
  certFileName: string,
): Promise<void> {
  if (!isMtlsEnabled()) {
    await app.listen(port);
    return;
  }

  const paths: MtlsPaths = getServiceCertPaths(certFileName);
  const server = https.createServer(readHttpsOptions(paths, true), app.getHttpAdapter().getInstance());
  await new Promise<void>((resolve) => server.listen(port, resolve));
}
