import type { SessionUser } from '../../../../packages/contracts/src/rbac.ts';

export interface HttpRequest {
  readonly method: string;
  readonly path: string;
  readonly params: Readonly<Record<string, string>>;
  readonly query: URLSearchParams;
  readonly body: unknown;
  readonly token: string | null;
  readonly user: SessionUser | null;
}

export interface HttpResponse {
  readonly status: number;
  readonly body: unknown;
}

export type RouteHandler = (request: HttpRequest) => HttpResponse | Promise<HttpResponse>;

export interface RouteDefinition {
  readonly method: string;
  /** Patron con parametros, p. ej. '/tasks/:id/reassign'. */
  readonly pattern: string;
  /** Permiso exigido. null = ruta publica. */
  readonly permission: string | null;
  readonly summary: string;
  readonly handler: RouteHandler;
}

export interface RouteMatch {
  readonly route: RouteDefinition;
  readonly params: Readonly<Record<string, string>>;
}

/** Enrutado por metodo + path, sin dependencias (node:http pelado). */
export class Router {
  // El campo NO puede llamarse 'routes': colisionaria con el metodo routes()
  // y el inicializador del campo pisaria el metodo en tiempo de ejecucion.
  private readonly definitions: RouteDefinition[] = [];

  add(route: RouteDefinition): void {
    this.definitions.push(route);
  }

  match(method: string, path: string): RouteMatch | null {
    const segments = path.split('/').filter((segment) => segment !== '');

    for (const route of this.definitions) {
      if (route.method !== method.toUpperCase()) continue;

      const patternSegments = route.pattern.split('/').filter((segment) => segment !== '');
      if (patternSegments.length !== segments.length) continue;

      const params: Record<string, string> = {};
      let matched = true;

      for (let index = 0; index < patternSegments.length; index += 1) {
        const pattern = patternSegments[index] ?? '';
        const segment = segments[index] ?? '';
        if (pattern.startsWith(':')) {
          params[pattern.slice(1)] = decodeURIComponent(segment);
        } else if (pattern !== segment) {
          matched = false;
          break;
        }
      }

      if (matched) return { route, params };
    }

    return null;
  }

  routes(): readonly RouteDefinition[] {
    return this.definitions;
  }

  /** Indice de rutas para GET /health y para la shell web. */
  describe(): readonly { method: string; pattern: string; permission: string | null; summary: string }[] {
    return this.definitions.map(({ method, pattern, permission, summary }) => ({
      method,
      pattern,
      permission,
      summary,
    }));
  }
}

export function json(status: number, body: unknown): HttpResponse {
  return { status, body };
}
