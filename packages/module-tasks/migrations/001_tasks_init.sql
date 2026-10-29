-- =====================================================================
-- TASKS · 001 · Motor de tareas dinámicas
-- Incluye el subesquema rules (motor ECA), propiedad de este módulo.
-- assignee_id / created_by_rule_id / store_id son referencias blandas.
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS rules;
COMMENT ON SCHEMA rules IS
  'Motor de reglas ECA (Evento-Condición-Acción). Subesquema del módulo de tareas.';

CREATE TYPE tasks.task_status AS ENUM ('PENDIENTE', 'ASIGNADA', 'EN_CURSO', 'BLOQUEADA', 'HECHA', 'CANCELADA');
CREATE TYPE tasks.task_priority AS ENUM ('BAJA', 'MEDIA', 'ALTA', 'URGENTE');
CREATE TYPE tasks.task_event_type AS ENUM (
  'CREADA', 'ASIGNADA', 'REASIGNADA', 'INICIADA', 'BLOQUEADA', 'DESBLOQUEADA',
  'COMPLETADA', 'CANCELADA', 'VENCIDA'
);

CREATE TYPE rules.execution_result AS ENUM (
  'DISPARADA', 'SIN_COINCIDENCIA', 'ERROR', 'OMITIDA_COOLDOWN', 'OMITIDA_LIMITE'
);

-- =====================================================================
-- tasks · Plantillas de tarea
-- =====================================================================
CREATE TABLE tasks.task_templates (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id           uuid NOT NULL,  -- referencia blanda a core.stores
  code               text NOT NULL,
  name               text NOT NULL,
  description        text,
  module             text NOT NULL DEFAULT 'tasks',
  default_priority   tasks.task_priority NOT NULL DEFAULT 'MEDIA',
  estimated_minutes  integer CHECK (estimated_minutes IS NULL OR estimated_minutes > 0),
  -- ROL MINIMO, no rol exclusivo. Una persona puede tomar la tarea si el nivel de
  -- su rol (core.roles.level) es >= el nivel del rol indicado aqui. Por eso una
  -- COORDINADORA (20) puede tomar una tarea marcada OPERADORA (10): en una tienda
  -- de alimentacion las encargadas reponen y cobran, no solo supervisan.
  required_role      text,  -- referencia blanda a core.roles.code
  checklist          jsonb NOT NULL DEFAULT '[]'::jsonb,
  sla_minutes        integer CHECK (sla_minutes IS NULL OR sla_minutes > 0),
  requires_evidence  boolean NOT NULL DEFAULT false,
  active             boolean NOT NULL DEFAULT true,
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now(),
  deleted_at         timestamptz,
  CONSTRAINT task_templates_checklist_array CHECK (jsonb_typeof(checklist) = 'array')
);
COMMENT ON TABLE tasks.task_templates IS
  'Catálogo de tareas que el motor de reglas puede instanciar mediante template_code.';

CREATE UNIQUE INDEX task_templates_code_uq ON tasks.task_templates (store_id, code) WHERE deleted_at IS NULL;
CREATE INDEX task_templates_active_idx ON tasks.task_templates (store_id) WHERE active AND deleted_at IS NULL;

-- =====================================================================
-- tasks · Tareas
-- =====================================================================
CREATE TABLE tasks.tasks (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id           uuid NOT NULL,  -- referencia blanda a core.stores
  template_id        uuid REFERENCES tasks.task_templates (id) ON DELETE SET NULL,
  title              text NOT NULL,
  description        text,
  priority           tasks.task_priority NOT NULL DEFAULT 'MEDIA',
  status             tasks.task_status NOT NULL DEFAULT 'PENDIENTE',
  assignee_id        uuid,  -- referencia blanda a core.users
  location_id        uuid,  -- referencia blanda a inventory.locations
  due_at             timestamptz,
  started_at         timestamptz,
  completed_at       timestamptz,
  cancelled_at       timestamptz,
  cancel_reason      text,
  created_by         uuid,  -- referencia blanda a core.users (NULL = generada por el sistema)
  created_by_rule_id uuid,  -- referencia blanda a rules.rules
  payload            jsonb NOT NULL DEFAULT '{}'::jsonb,
  evidence           jsonb NOT NULL DEFAULT '[]'::jsonb,
  parent_task_id     uuid REFERENCES tasks.tasks (id) ON DELETE SET NULL,
  -- Bloqueo optimista del Kanban. Con tres coordinadoras moviendo tarjetas a la vez
  -- (sobre todo en el traspaso de turno), dos reasignaciones simultaneas sobre la
  -- misma tarea se resolverian como "el ultimo gana", en silencio: una coordinadora
  -- creeria haber asignado la tarea a Ana cuando otra ya la movio a Rocio.
  -- Quien reasigna envia la version que leyo; si ya no coincide, se RECHAZA con aviso.
  version            integer NOT NULL DEFAULT 1 CHECK (version > 0),
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now(),
  deleted_at         timestamptz,
  CONSTRAINT tasks_payload_object CHECK (jsonb_typeof(payload) = 'object'),
  CONSTRAINT tasks_evidence_array CHECK (jsonb_typeof(evidence) = 'array'),
  CONSTRAINT tasks_completed_consistency CHECK (status <> 'HECHA' OR completed_at IS NOT NULL)
);

-- El Kanban NO almacena columnas: se derivan del status.
CREATE INDEX tasks_board_idx
  ON tasks.tasks (store_id, status, priority, due_at) WHERE deleted_at IS NULL;
CREATE INDEX tasks_assignee_idx
  ON tasks.tasks (store_id, assignee_id, status) WHERE deleted_at IS NULL;
-- Índice parcial para la detección de tareas vencidas (evento tasks.overdue).
CREATE INDEX tasks_overdue_idx
  ON tasks.tasks (due_at)
  WHERE status NOT IN ('HECHA', 'CANCELADA') AND deleted_at IS NULL;
CREATE INDEX tasks_template_idx ON tasks.tasks (template_id);
CREATE INDEX tasks_location_idx ON tasks.tasks (location_id);
CREATE INDEX tasks_parent_idx ON tasks.tasks (parent_task_id);
CREATE INDEX tasks_rule_idx ON tasks.tasks (created_by_rule_id) WHERE created_by_rule_id IS NOT NULL;
CREATE INDEX tasks_created_idx ON tasks.tasks (store_id, created_at DESC);

-- =====================================================================
-- tasks · Historial de la tarea (append-only)
-- =====================================================================
CREATE TABLE tasks.task_events (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id      uuid NOT NULL REFERENCES tasks.tasks (id) ON DELETE CASCADE,
  store_id     uuid NOT NULL,  -- referencia blanda a core.stores
  type         tasks.task_event_type NOT NULL,
  from_user_id uuid,  -- referencia blanda a core.users
  to_user_id   uuid,  -- referencia blanda a core.users
  from_status  tasks.task_status,
  to_status    tasks.task_status,
  comment      text,
  payload      jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT task_events_payload_object CHECK (jsonb_typeof(payload) = 'object')
);
COMMENT ON TABLE tasks.task_events IS
  'Tabla append-only: solo INSERT. Sin este historial nadie sabe quién movió una tarea ni por qué.';

CREATE INDEX task_events_task_idx ON tasks.task_events (task_id, created_at);
CREATE INDEX task_events_to_user_idx ON tasks.task_events (to_user_id, created_at DESC);
CREATE INDEX task_events_type_idx ON tasks.task_events (store_id, type, created_at DESC);

-- =====================================================================
-- rules · Reglas ECA (event_type + condition JSONB + actions JSONB)
-- =====================================================================
CREATE TABLE rules.rules (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id         uuid NOT NULL,  -- referencia blanda a core.stores
  code             text NOT NULL,
  name             text NOT NULL,
  description      text,
  event_type       text NOT NULL,
  condition        jsonb NOT NULL DEFAULT '{"all": []}'::jsonb,
  actions          jsonb NOT NULL DEFAULT '[]'::jsonb,
  priority         integer NOT NULL DEFAULT 100,
  version          integer NOT NULL DEFAULT 1 CHECK (version > 0),
  is_active        boolean NOT NULL DEFAULT false,
  cooldown_minutes integer NOT NULL DEFAULT 0 CHECK (cooldown_minutes >= 0),
  max_per_day      integer CHECK (max_per_day IS NULL OR max_per_day > 0),
  valid_from       timestamptz,
  valid_to         timestamptz,
  created_by       uuid,  -- referencia blanda a core.users
  updated_by       uuid,  -- referencia blanda a core.users
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now(),
  deleted_at       timestamptz,
  CONSTRAINT rules_condition_object CHECK (jsonb_typeof(condition) = 'object'),
  CONSTRAINT rules_actions_array CHECK (jsonb_typeof(actions) = 'array'),
  CONSTRAINT rules_actions_not_empty CHECK (jsonb_array_length(actions) > 0),
  CONSTRAINT rules_valid_range CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to > valid_from)
);
COMMENT ON COLUMN rules.rules.condition IS
  'Árbol evaluable: {"all":[{"fact":"...","op":"...","value":...}]}. JSONB y no EAV: es un documento anidado que se evalua en memoria.';
COMMENT ON COLUMN rules.rules.actions IS
  'Lista ordenada: [{"type":"CREATE_TASK","params":{...}}]. Cada modulo registra sus propias acciones.';

CREATE UNIQUE INDEX rules_code_uq ON rules.rules (store_id, code) WHERE deleted_at IS NULL;
-- Índice parcial: el evaluador solo mira reglas activas de un tipo de evento.
CREATE INDEX rules_active_idx
  ON rules.rules (store_id, event_type, priority) WHERE is_active AND deleted_at IS NULL;
CREATE INDEX rules_condition_gin ON rules.rules USING gin (condition jsonb_path_ops);
CREATE INDEX rules_actions_gin ON rules.rules USING gin (actions jsonb_path_ops);

-- ---------------------------------------------------------------------
-- rules · Ejecuciones (append-only): auditoría de cada decisión del motor
-- ---------------------------------------------------------------------
CREATE TABLE rules.rule_executions (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id          uuid NOT NULL REFERENCES rules.rules (id) ON DELETE CASCADE,
  rule_version     integer NOT NULL,
  store_id         uuid NOT NULL,  -- referencia blanda a core.stores
  event_id         uuid,  -- referencia blanda a core.outbox_events
  event_type       text NOT NULL,
  context          jsonb NOT NULL DEFAULT '{}'::jsonb,
  matched          boolean NOT NULL DEFAULT false,
  actions_executed jsonb NOT NULL DEFAULT '[]'::jsonb,
  result           rules.execution_result NOT NULL DEFAULT 'SIN_COINCIDENCIA',
  error            text,
  duration_ms      integer CHECK (duration_ms IS NULL OR duration_ms >= 0),
  created_at       timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT rule_executions_context_object CHECK (jsonb_typeof(context) = 'object'),
  CONSTRAINT rule_executions_actions_array CHECK (jsonb_typeof(actions_executed) = 'array')
);
COMMENT ON TABLE rules.rule_executions IS
  'Tabla append-only: solo INSERT. Guarda la version de la regla usada, para auditar decisiones historicas.';

CREATE INDEX rule_executions_rule_idx ON rules.rule_executions (rule_id, created_at DESC);
CREATE INDEX rule_executions_event_idx ON rules.rule_executions (event_id);
CREATE INDEX rule_executions_created_idx ON rules.rule_executions (store_id, created_at DESC);
CREATE INDEX rule_executions_failed_idx
  ON rules.rule_executions (store_id, created_at DESC) WHERE result = 'ERROR';

-- ---------------------------------------------------------------------
-- rules · Sobrescrituras tácticas de las coordinadoras
-- ---------------------------------------------------------------------
CREATE TABLE rules.rule_overrides (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id       uuid NOT NULL,  -- referencia blanda a core.stores
  rule_id        uuid NOT NULL REFERENCES rules.rules (id) ON DELETE CASCADE,
  override_date  date NOT NULL,
  target_user_id uuid,  -- referencia blanda a core.users
  action_type    text,
  reason         text NOT NULL,
  by_user_id     uuid NOT NULL,  -- referencia blanda a core.users
  expires_at     timestamptz,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT rule_overrides_reason_not_blank CHECK (btrim(reason) <> '')
);
COMMENT ON TABLE rules.rule_overrides IS
  'Permite a coordinación forzar la asignación de un día concreto sin poder modificar la regla.';

CREATE INDEX rule_overrides_rule_idx ON rules.rule_overrides (rule_id, override_date);
CREATE INDEX rule_overrides_target_idx ON rules.rule_overrides (target_user_id);
CREATE UNIQUE INDEX rule_overrides_uq
  ON rules.rule_overrides (rule_id, override_date, COALESCE(target_user_id, '00000000-0000-0000-0000-000000000000'::uuid));

-- ---------------------------------------------------------------------
-- Bloqueo optimista de tasks.tasks
-- La columna version por si sola no protege de nada: hace falta que la base
-- garantice que SIEMPRE avanza exactamente de uno en uno. Asi el cliente puede
-- reasignar con "where id = ? and version = <la que leyo>" y, si otra
-- coordinadora se le adelanto, la sentencia afecta a 0 filas en lugar de pisar
-- el cambio en silencio.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION tasks.bump_version()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.version = OLD.version THEN
    -- El cliente no la incremento: lo hace la base por el.
    NEW.version := OLD.version + 1;
  ELSIF NEW.version <> OLD.version + 1 THEN
    RAISE EXCEPTION 'tasks.tasks.version invalida: se esperaba % (sin cambio) o % (incremento de uno), llego %',
      OLD.version, OLD.version + 1, NEW.version
      USING ERRCODE = 'restrict_violation';
  END IF;
  RETURN NEW;
END;
$$;
COMMENT ON FUNCTION tasks.bump_version() IS
  'Trigger BEFORE UPDATE: garantiza que tasks.tasks.version avanza exactamente de uno en uno. Es lo que hace fiable el bloqueo optimista del Kanban.';

CREATE TRIGGER trg_tasks_version
  BEFORE UPDATE ON tasks.tasks
  FOR EACH ROW EXECUTE FUNCTION tasks.bump_version();

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_task_templates_updated_at
  BEFORE UPDATE ON tasks.task_templates
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_tasks_updated_at
  BEFORE UPDATE ON tasks.tasks
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_rules_updated_at
  BEFORE UPDATE ON rules.rules
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_rule_overrides_updated_at
  BEFORE UPDATE ON rules.rule_overrides
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();

-- ---------------------------------------------------------------------
-- Inmutabilidad
-- ---------------------------------------------------------------------
REVOKE UPDATE, DELETE ON tasks.task_events FROM PUBLIC;
REVOKE UPDATE, DELETE ON rules.rule_executions FROM PUBLIC;

CREATE TRIGGER trg_task_events_immutable
  BEFORE UPDATE OR DELETE ON tasks.task_events
  FOR EACH ROW EXECUTE FUNCTION util.forbid_mutation();
CREATE TRIGGER trg_rule_executions_immutable
  BEFORE UPDATE OR DELETE ON rules.rule_executions
  FOR EACH ROW EXECUTE FUNCTION util.forbid_mutation();
