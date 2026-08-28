import * as fs from 'fs';
import * as https from 'https';
import * as path from 'path';

export interface MtlsPaths {
  cert: string;
  key: string;
  ca: string;
}

export function resolveCertsDir(): string {
  const fromEnv = process.env.CERTS_DIR;
  if (fromEnv) {
    return path.resolve(fromEnv);
  }
  const candidates = [
    path.resolve(process.cwd(), 'docker/certs'),
    path.resolve(process.cwd(), '../../docker/certs'),
  ];
  for (const dir of candidates) {
    if (fs.existsSync(path.join(dir, 'ca.crt'))) {
      return dir;
    }
  }
  return candidates[0];
}

export function getServiceCertPaths(serviceFileName: string): MtlsPaths {
  const dir = resolveCertsDir();
  return {
    cert: path.join(dir, `${serviceFileName}.crt`),
    key: path.join(dir, `${serviceFileName}.key`),
    ca: path.join(dir, 'ca.crt'),
  };
}

export function createMtlsAgent(paths: MtlsPaths): https.Agent {
  return new https.Agent({
    cert: fs.readFileSync(paths.cert),
    key: fs.readFileSync(paths.key),
    ca: fs.readFileSync(paths.ca),
    rejectUnauthorized: true,
  });
}

export function readHttpsOptions(paths: MtlsPaths, requestCert = true): https.ServerOptions {
  return {
    cert: fs.readFileSync(paths.cert),
    key: fs.readFileSync(paths.key),
    ca: fs.readFileSync(paths.ca),
    requestCert,
    rejectUnauthorized: requestCert,
  };
}

export function isMtlsEnabled(): boolean {
  return process.env.MTLS_ENABLED !== 'false';
}
