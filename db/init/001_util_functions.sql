-- =====================================================================
-- 001 · Funciones de utilidad usadas por los triggers de todos los módulos
-- =====================================================================

-- Mantiene updated_at en cada UPDATE.
CREATE OR REPLACE FUNCTION util.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION util.set_updated_at() IS
  'Trigger BEFORE UPDATE: fija updated_at = now(). Obligatorio en toda tabla con updated_at.';

-- Bloquea cualquier UPDATE o DELETE. Se usa en las tablas append-only.
CREATE OR REPLACE FUNCTION util.forbid_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'La tabla %.% es de solo inserción (append-only)', TG_TABLE_SCHEMA, TG_TABLE_NAME
    USING ERRCODE = 'restrict_violation';
  RETURN NULL;
END;
$$;

COMMENT ON FUNCTION util.forbid_mutation() IS
  'Trigger BEFORE UPDATE OR DELETE: aborta la operación. Complementa el REVOKE sobre las tablas append-only.';

-- En core.outbox_events el relay DEBE poder marcar el estado de entrega,
-- pero el contenido del evento (payload y claves del agregado) es inmutable.
CREATE OR REPLACE FUNCTION util.forbid_outbox_payload_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.event_type     IS DISTINCT FROM OLD.event_type
     OR NEW.aggregate_type IS DISTINCT FROM OLD.aggregate_type
     OR NEW.aggregate_id   IS DISTINCT FROM OLD.aggregate_id
     OR NEW.payload        IS DISTINCT FROM OLD.payload
     OR NEW.store_id       IS DISTINCT FROM OLD.store_id
     OR NEW.created_at     IS DISTINCT FROM OLD.created_at THEN
    RAISE EXCEPTION 'core.outbox_events: el contenido del evento es inmutable'
      USING ERRCODE = 'restrict_violation';
  END IF;
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION util.forbid_outbox_payload_change() IS
  'Trigger BEFORE UPDATE en el outbox: solo permite actualizar status, retries, last_error, available_at y processed_at.';
