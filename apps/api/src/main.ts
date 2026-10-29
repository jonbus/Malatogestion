import { createServer } from 'node:http';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { createSystem } from './composition-root.ts';
import type { LogLevel, SystemRuntime } from './composition-root.ts';
import { authorize } from './http/rbac-guard.ts';
import type { HttpResponse } from './http/router.ts';

const PORT = Number(process.env['PORT'] ?? 3000);
const HOST = process.env['HOST'] ?? '127.0.0.1';
const LOG_LEVEL = (process.env['LOG_LEVEL'] ?? 'info') as LogLevel;

const system: SystemRuntime = createSystem({ loadRulesFromSeed: true, logLevel: LOG_LEVEL });

function bearerToken(header: string | undefined): string | null {
  if (!header) return null;
  const [scheme, value] = header.split(' ');
  if (scheme?.toLowerCase() !== 'bearer' || !value) return null;
  return value;
}

async function readBody(request: IncomingMessage): Promise<unknown> {
  const method = (request.method ?? 'GET').toUpperCase();
  if (method === 'GET' || method === 'HEAD' || method === 'DELETE') return null;

  const chunks: Buffer[] = [];
  for await (const chunk of request) chunks.push(chunk as Buffer);
  if (chunks.length === 0) return null;

  const raw = Buffer.concat(chunks).toString('utf8').trim();
  if (raw === '') return null;

  try {
    return JSON.parse(raw);
  } catch {
    return { __error: 'JSON_INVALIDO' };
  }
}

function send(response: ServerResponse, result: HttpResponse): void {
  if (result.status === 204 || result.body === null || result.body === undefined) {
    response.writeHead(result.status === 204 ? 204 : result.status);
    response.end();
    return;
  }

  const payload = JSON.stringify(result.body);
  response.writeHead(result.status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(payload),
  });
  response.end(payload);
}

const server = createServer((request, response) => {
  void (async () => {
    try {
      const method = (request.method ?? 'GET').toUpperCase();
      const url = new URL(request.url ?? '/', `http://${request.headers.host ?? 'localhost'}`);

      const match = system.router.match(method, url.pathname);
      if (!match) {
        send(response, {
          status: 404,
          body: { error: 'RUTA_NO_ENCONTRADA', path: url.pathname, rutas: system.router.describe() },
        });
        return;
      }

      const token = bearerToken(request.headers.authorization) ?? url.searchParams.get('token');
      const user = system.auth.resolve(token);

      const outcome = authorize(match.route, user, system.registry);
      if (!outcome.allowed) {
        send(response, { status: outcome.status, body: outcome.body });
        return;
      }

      const body = await readBody(request);
      const result = await match.route.handler({
        method,
        path: url.pathname,
        params: match.params,
        query: url.searchParams,
        body,
        token,
        user,
      });

      send(response, result);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : String(cause);
      system.logger.error('Error no controlado en HTTP', { error: message });
      send(response, { status: 500, body: { error: 'ERROR_INTERNO', detail: message } });
    }
  })();
});

server.listen(PORT, HOST, () => {
  system.logger.info('API escuchando (host sin logica de negocio)', {
    url: `http://${HOST}:${PORT}`,
    modules: system.registry.count(),
    rules: system.ruleRepository.size(),
  });
});

function shutdown(signal: string): void {
  system.logger.info('Apagando', { signal });
  server.close(() => process.exit(0));
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
