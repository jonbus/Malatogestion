-- =====================================================================
-- CORE · 001 · Identidad, RBAC, auditoría, outbox y configuración
-- Depende de: db/init/000, db/init/001. No depende de ningún módulo.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tipos
-- ---------------------------------------------------------------------
CREATE TYPE core.outbox_status AS ENUM ('PENDIENTE', 'PROCESADO', 'FALLIDO', 'DESCARTADO');

-- ---------------------------------------------------------------------
-- Tiendas
-- ---------------------------------------------------------------------
CREATE TABLE core.stores (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code       text NOT NULL UNIQUE,
  name       text NOT NULL,
  address    jsonb NOT NULL DEFAULT '{}'::jsonb,
  timezone   text NOT NULL DEFAULT 'Europe/Madrid',
  currency   char(3) NOT NULL DEFAULT 'EUR',
  active     boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  CONSTRAINT stores_address_object CHECK (jsonb_typeof(address) = 'object')
);
COMMENT ON TABLE core.stores IS
  'Tiendas. store_id se propaga a todo lo operativo como referencia blanda, sin FK.';

-- ---------------------------------------------------------------------
-- RBAC: roles, permisos por acción y excepciones por usuario
-- ---------------------------------------------------------------------
CREATE TABLE core.roles (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code        text NOT NULL UNIQUE,
  name        text NOT NULL,
  description text,
  is_system   boolean NOT NULL DEFAULT false,
  -- Nivel jerarquico. Es lo que permite COMPARAR roles entre si en lugar de
  -- tratarlos como conjuntos disjuntos: una persona puede tomar cualquier tarea
  -- cuyo rol requerido tenga nivel menor o igual que el suyo.
  -- GERENCIA 30 > COORDINADORA 20 > OPERADORA 10.
  -- Sin valor por defecto a proposito: un rol nuevo debe declarar su nivel de
  -- forma explicita, no heredar 0 (que lo dejaria sin poder tomar nada) por olvido.
  level       smallint NOT NULL CHECK (level >= 0),
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
COMMENT ON COLUMN core.roles.code IS
  'GERENCIA | COORDINADORA | OPERADORA. Un rol nuevo es una fila nueva, no un despliegue.';
COMMENT ON COLUMN core.roles.level IS
  'Jerarquia: GERENCIA=30, COORDINADORA=20, OPERADORA=10. El nivel del rol de una persona debe ser >= el nivel del rol requerido por la tarea para poder tomarla. Los roles son jerarquicos, no excluyentes: quien coordina tambien repone y cobra.';

CREATE TABLE core.permissions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code        text NOT NULL UNIQUE,
  module      text NOT NULL,
  description text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
COMMENT ON COLUMN core.permissions.code IS 'Formato modulo.accion, p.ej. tasks.reassign.';
CREATE INDEX permissions_module_idx ON core.permissions (module);

CREATE TABLE core.role_permissions (
  role_id       uuid NOT NULL REFERENCES core.roles (id) ON DELETE CASCADE,
  permission_id uuid NOT NULL REFERENCES core.permissions (id) ON DELETE CASCADE,
  created_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (role_id, permission_id)
);
CREATE INDEX role_permissions_permission_idx ON core.role_permissions (permission_id);

-- ---------------------------------------------------------------------
-- Usuarios
-- ---------------------------------------------------------------------
CREATE TABLE core.users (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id      uuid NOT NULL,  -- referencia blanda a core.stores
  email         citext NOT NULL,
  password_hash text,
  full_name     text NOT NULL,
  role_id       uuid NOT NULL REFERENCES core.roles (id) ON DELETE RESTRICT,
  pin_caja      text,           -- hash del PIN de caja; nunca el PIN en claro
  phone         text,
  active        boolean NOT NULL DEFAULT true,
  last_login_at timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  deleted_at    timestamptz
);
COMMENT ON COLUMN core.users.pin_caja IS
  'Hash del PIN de 4 dígitos (argon2id/bcrypt). No se indexa como UNIQUE porque el hash lleva salt.';

CREATE UNIQUE INDEX users_email_uq ON core.users (email) WHERE deleted_at IS NULL;
CREATE INDEX users_role_idx ON core.users (role_id);
CREATE INDEX users_store_role_idx ON core.users (store_id, role_id) WHERE deleted_at IS NULL;
CREATE INDEX users_active_idx ON core.users (store_id) WHERE active AND deleted_at IS NULL;

-- Excepciones puntuales sobre el rol (conceder o revocar una acción concreta).
CREATE TABLE core.user_permissions (
  user_id       uuid NOT NULL REFERENCES core.users (id) ON DELETE CASCADE,
  permission_id uuid NOT NULL REFERENCES core.permissions (id) ON DELETE CASCADE,
  granted       boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, permission_id)
);
CREATE INDEX user_permissions_permission_idx ON core.user_permissions (permission_id);

-- ---------------------------------------------------------------------
-- Auditoría (append-only)
-- ---------------------------------------------------------------------
CREATE TABLE core.audit_log (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id   uuid,
  actor_id   uuid,       -- referencia blanda a core.users (puede ser NULL si actúa el sistema)
  actor_role text,
  module     text NOT NULL,
  action     text NOT NULL,
  ref_type   text,
  ref_id     uuid,
  before     jsonb,
  after      jsonb,
  ip         inet,
  user_agent text,
  created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.audit_log IS
  'Tabla append-only: solo INSERT. Traza inmutable de toda acción del sistema y de los usuarios.';

CREATE INDEX audit_log_ref_idx ON core.audit_log (ref_type, ref_id);
CREATE INDEX audit_log_actor_idx ON core.audit_log (actor_id, created_at DESC);
CREATE INDEX audit_log_module_idx ON core.audit_log (module, action, created_at DESC);
CREATE INDEX audit_log_created_idx ON core.audit_log (created_at DESC);

-- ---------------------------------------------------------------------
-- Outbox transaccional (patrón outbox del bus de eventos)
-- ---------------------------------------------------------------------
CREATE TABLE core.outbox_events (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id       uuid,
  event_type     text NOT NULL,
  aggregate_type text NOT NULL,
  aggregate_id   uuid,
  payload        jsonb NOT NULL,
  status         core.outbox_status NOT NULL DEFAULT 'PENDIENTE',
  retries        integer NOT NULL DEFAULT 0 CHECK (retries >= 0),
  last_error     text,
  available_at   timestamptz NOT NULL DEFAULT now(),
  created_at     timestamptz NOT NULL DEFAULT now(),
  processed_at   timestamptz,
  CONSTRAINT outbox_payload_object CHECK (jsonb_typeof(payload) = 'object')
);
COMMENT ON TABLE core.outbox_events IS
  'El evento se inserta en la MISMA transacción que el cambio de estado. El contenido es inmutable; el relay solo actualiza status, retries, last_error, available_at y processed_at.';

-- Índice parcial: el relay solo busca lo pendiente y ya disponible.
CREATE INDEX outbox_pending_idx ON core.outbox_events (available_at, created_at) WHERE status = 'PENDIENTE';
CREATE INDEX outbox_type_idx ON core.outbox_events (event_type, created_at DESC);
CREATE INDEX outbox_aggregate_idx ON core.outbox_events (aggregate_type, aggregate_id);

-- ---------------------------------------------------------------------
-- Configuración por tienda o global (store_id NULL = global)
-- ---------------------------------------------------------------------
CREATE TABLE core.settings (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid,
  key         text NOT NULL,
  module      text NOT NULL,
  value       jsonb NOT NULL DEFAULT '{}'::jsonb,
  description text,
  updated_by  uuid,   -- referencia blanda a core.users
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT settings_value_object CHECK (jsonb_typeof(value) = 'object')
);
CREATE UNIQUE INDEX settings_scope_uq
  ON core.settings (COALESCE(store_id, '00000000-0000-0000-0000-000000000000'::uuid), key);
CREATE INDEX settings_module_idx ON core.settings (module);

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_stores_updated_at
  BEFORE UPDATE ON core.stores
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_roles_updated_at
  BEFORE UPDATE ON core.roles
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_permissions_updated_at
  BEFORE UPDATE ON core.permissions
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON core.users
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_user_permissions_updated_at
  BEFORE UPDATE ON core.user_permissions
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_settings_updated_at
  BEFORE UPDATE ON core.settings
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();

-- ---------------------------------------------------------------------
-- Inmutabilidad
-- ---------------------------------------------------------------------
REVOKE UPDATE, DELETE ON core.audit_log FROM PUBLIC;
REVOKE DELETE ON core.outbox_events FROM PUBLIC;  -- el relay debe poder marcar el estado

CREATE TRIGGER trg_audit_log_immutable
  BEFORE UPDATE OR DELETE ON core.audit_log
  FOR EACH ROW EXECUTE FUNCTION util.forbid_mutation();
CREATE TRIGGER trg_outbox_no_delete
  BEFORE DELETE ON core.outbox_events
  FOR EACH ROW EXECUTE FUNCTION util.forbid_mutation();
CREATE TRIGGER trg_outbox_payload_immutable
  BEFORE UPDATE ON core.outbox_events
  FOR EACH ROW EXECUTE FUNCTION util.forbid_outbox_payload_change();
