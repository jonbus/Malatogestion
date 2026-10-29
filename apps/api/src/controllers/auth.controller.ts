import { randomBytes } from 'node:crypto';
import type { SessionUser } from '../../../../packages/contracts/src/rbac.ts';
import { json } from '../http/router.ts';
import type { HttpResponse, Router } from '../http/router.ts';

export interface AuthUser {
  readonly session: SessionUser;
  readonly email: string;
  /** PIN de 4 digitos. En produccion se guarda hasheado (argon2id) en core.users. */
  readonly pin: string;
}

interface Session {
  readonly token: string;
  readonly user: SessionUser;
  readonly createdAt: string;
  lastSeenAt: string;
}

/**
 * Autenticacion por PIN con token de sesion en memoria.
 * El Bloque 0 no persiste sesiones: en produccion serian filas en core y un
 * token firmado. La interfaz (token opaco) no cambia.
 */
export class AuthController {
  private readonly users: readonly AuthUser[];
  private readonly sessions = new Map<string, Session>();

  constructor(users: readonly AuthUser[]) {
    this.users = users;
  }

  resolve(token: string | null): SessionUser | null {
    if (!token) return null;
    const session = this.sessions.get(token);
    if (!session) return null;
    session.lastSeenAt = new Date().toISOString();
    return session.user;
  }

  login(body: unknown): HttpResponse {
    if (typeof body !== 'object' || body === null) {
      return json(400, { error: 'CUERPO_INVALIDO' });
    }

    const payload = body as Record<string, unknown>;
    const pin = typeof payload['pin'] === 'string' ? payload['pin'] : '';
    const email = typeof payload['email'] === 'string' ? payload['email'].toLowerCase() : null;

    if (pin === '') return json(400, { error: 'PIN_REQUERIDO' });

    const candidates = this.users.filter((user) => user.pin === pin);
    const found = email
      ? candidates.find((user) => user.email.toLowerCase() === email)
      : candidates.length === 1
        ? candidates[0]
        : undefined;

    if (!found) {
      return json(401, {
        error: 'CREDENCIALES_INVALIDAS',
        detail: candidates.length > 1 ? 'Ese PIN es compartido: indica tambien el email' : undefined,
      });
    }

    const token = randomBytes(24).toString('hex');
    this.sessions.set(token, {
      token,
      user: found.session,
      createdAt: new Date().toISOString(),
      lastSeenAt: new Date().toISOString(),
    });

    return json(200, { token, user: found.session });
  }

  logout(token: string | null): HttpResponse {
    if (token) this.sessions.delete(token);
    return json(204, null);
  }

  activeSessions(): number {
    return this.sessions.size;
  }

  register(router: Router): void {
    router.add({
      method: 'POST',
      pattern: '/auth/login',
      permission: null,
      summary: 'Inicio de sesion por PIN',
      handler: (request) => this.login(request.body),
    });

    router.add({
      method: 'POST',
      pattern: '/auth/logout',
      permission: null,
      summary: 'Cierre de sesion',
      handler: (request) => this.logout(request.token),
    });
  }
}
