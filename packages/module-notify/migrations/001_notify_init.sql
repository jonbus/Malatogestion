-- =====================================================================
-- NOTIFY · 001 · Notificaciones y suscripciones por usuario
-- target_user_id / target_role / ref_id son referencias blandas.
-- =====================================================================

CREATE TYPE notify.severity AS ENUM ('INFO', 'AVISO', 'GRAVE', 'CRITICO');

-- ---------------------------------------------------------------------
-- Notificaciones
-- ---------------------------------------------------------------------
CREATE TABLE notify.notifications (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id       uuid NOT NULL,  -- referencia blanda a core.stores
  type           text NOT NULL,  -- coincide con el event_type que la origina
  severity       notify.severity NOT NULL DEFAULT 'INFO',
  title          text NOT NULL,
  body           text,
  payload        jsonb NOT NULL DEFAULT '{}'::jsonb,
  target_role    text,  -- referencia blanda a core.roles.code
  target_user_id uuid,  -- referencia blanda a core.users
  ref_type       text,
  ref_id         uuid,
  dedup_key      text,  -- evita repetir el mismo aviso
  created_at     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT notifications_payload_object CHECK (jsonb_typeof(payload) = 'object'),
  CONSTRAINT notifications_has_target CHECK (target_role IS NOT NULL OR target_user_id IS NOT NULL)
);
COMMENT ON COLUMN notify.notifications.dedup_key IS
  'Clave de deduplicacion por tienda: impide que un evento repetido genere avisos duplicados.';
-- NO existe read_at global. Con target_role = 'COORDINADORA' y tres coordinadoras,
-- una sola columna read_at hacia que la primera que abria el aviso lo marcara leido
-- para las tres: o las otras dos no lo veian (y podia ser justo la que debia actuar),
-- o las tres actuaban y triplicaban el trabajo. El estado de lectura es POR PERSONA
-- y vive en notify.notification_reads.

CREATE UNIQUE INDEX notifications_dedup_uq
  ON notify.notifications (store_id, dedup_key) WHERE dedup_key IS NOT NULL;
-- Bandeja de entrada. Estos indices YA NO son parciales por read_at: el estado de
-- lectura vive en otra tabla y un predicado parcial no puede consultarla. El filtro
-- de "no leido" se resuelve con un anti-join contra notification_reads, que tiene su
-- propio indice por usuario.
CREATE INDEX notifications_inbox_user_idx
  ON notify.notifications (target_user_id, created_at DESC);
CREATE INDEX notifications_inbox_role_idx
  ON notify.notifications (store_id, target_role, created_at DESC);
CREATE INDEX notifications_severity_idx ON notify.notifications (store_id, severity, created_at DESC);
CREATE INDEX notifications_type_idx ON notify.notifications (type, created_at DESC);
CREATE INDEX notifications_ref_idx ON notify.notifications (ref_type, ref_id);
CREATE INDEX notifications_payload_gin ON notify.notifications USING gin (payload jsonb_path_ops);

-- ---------------------------------------------------------------------
-- Estado de lectura POR USUARIO
-- Una notificacion dirigida a un rol la ven varias personas y cada una la atiende
-- cuando puede. Que una la lea NO la marca leida para las demas: genera su propia
-- fila. Es lo que evita que el aviso desaparezca para quien aun no lo ha visto.
-- ---------------------------------------------------------------------
CREATE TABLE notify.notification_reads (
  notification_id uuid NOT NULL REFERENCES notify.notifications (id) ON DELETE CASCADE,
  user_id         uuid NOT NULL,  -- referencia blanda a core.users
  read_at         timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (notification_id, user_id)
);
COMMENT ON TABLE notify.notification_reads IS
  'Estado de lectura por persona. Una fila por (notificacion, usuario). La ausencia de fila significa NO LEIDA para ese usuario.';

CREATE INDEX notification_reads_user_idx ON notify.notification_reads (user_id, read_at DESC);
CREATE INDEX notification_reads_notification_idx ON notify.notification_reads (notification_id);

-- ---------------------------------------------------------------------
-- Suscripciones: qué avisos quiere recibir cada usuario y por qué canal
-- ---------------------------------------------------------------------
CREATE TABLE notify.notification_subscriptions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid NOT NULL,  -- referencia blanda a core.stores
  user_id     uuid NOT NULL,  -- referencia blanda a core.users
  type        text NOT NULL,  -- '*' = todos los avisos
  channels    jsonb NOT NULL DEFAULT '["IN_APP"]'::jsonb,
  quiet_hours jsonb,
  enabled     boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT notification_subscriptions_channels_array CHECK (jsonb_typeof(channels) = 'array')
);
COMMENT ON COLUMN notify.notification_subscriptions.quiet_hours IS
  'Franja sin avisos no críticos, p.ej. {"from":"22:00","to":"07:00"}.';

CREATE UNIQUE INDEX notification_subscriptions_uq ON notify.notification_subscriptions (user_id, type);
CREATE INDEX notification_subscriptions_user_idx
  ON notify.notification_subscriptions (user_id) WHERE enabled;

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_notification_subscriptions_updated_at
  BEFORE UPDATE ON notify.notification_subscriptions
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
