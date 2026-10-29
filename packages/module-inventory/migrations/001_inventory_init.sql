-- =====================================================================
-- INVENTORY · 001 · Ubicaciones, stock, lotes, movimientos y mermas
-- product_id / store_id / user_id son referencias blandas: sin FK.
-- =====================================================================

CREATE TYPE inventory.location_type AS ENUM ('SALA', 'ALMACEN', 'CAMARA', 'CAJA', 'DEVOLUCIONES');
CREATE TYPE inventory.movement_type AS ENUM ('ENTRADA', 'SALIDA', 'AJUSTE', 'MERMA', 'DEVOLUCION', 'TRASPASO');
CREATE TYPE inventory.wastage_reason AS ENUM ('CADUCADO', 'ROTO', 'MERMA_DESCONOCIDA', 'ROBO', 'ERROR_RECEPCION');

-- ---------------------------------------------------------------------
-- Ubicaciones físicas
-- ---------------------------------------------------------------------
CREATE TABLE inventory.locations (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id   uuid NOT NULL,  -- referencia blanda a core.stores
  code       text NOT NULL,
  name       text NOT NULL,
  type       inventory.location_type NOT NULL,
  active     boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz
);
CREATE UNIQUE INDEX locations_code_uq ON inventory.locations (store_id, code) WHERE deleted_at IS NULL;
CREATE INDEX locations_type_idx ON inventory.locations (store_id, type) WHERE deleted_at IS NULL;

-- ---------------------------------------------------------------------
-- Saldo de stock (lectura rápida). La verdad inmutable son los movimientos.
-- ---------------------------------------------------------------------
CREATE TABLE inventory.stock (
  product_id   uuid NOT NULL,  -- referencia blanda a catalog.products
  location_id  uuid NOT NULL REFERENCES inventory.locations (id) ON DELETE RESTRICT,
  store_id     uuid NOT NULL,  -- referencia blanda a core.stores
  qty          numeric(14,3) NOT NULL DEFAULT 0 CHECK (qty >= 0),
  reserved_qty numeric(14,3) NOT NULL DEFAULT 0 CHECK (reserved_qty >= 0),
  -- Mientras la app no integre el cobro, `qty` es una CREENCIA, no un hecho: nadie
  -- descuenta lo vendido. last_counted_at distingue "contado hoy y hay 0" de
  -- "nunca contado y pone 0", que son dos situaciones opuestas. Sin esta columna el
  -- motor de reglas no puede saber si el stock que lee merece credito.
  -- Si en el futuro se integra el TPV, esta columna pasa a ser prescindible.
  last_counted_at timestamptz,
  count_source text CHECK (count_source IS NULL OR count_source IN
    ('RECUENTO', 'RECEPCION', 'AJUSTE', 'MERMA', 'IMPORTACION_TPV')),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (product_id, location_id),
  CONSTRAINT stock_reserved_lte_qty CHECK (reserved_qty <= qty)
);
COMMENT ON TABLE inventory.stock IS
  'Saldo actual por producto y ubicación. Si diverge de stock_movements, se reconstruye desde los movimientos.';

CREATE INDEX stock_location_idx ON inventory.stock (location_id);
CREATE INDEX stock_store_idx ON inventory.stock (store_id);

-- ---------------------------------------------------------------------
-- Lotes y caducidades (obligatorio en perecederos)
-- ---------------------------------------------------------------------
CREATE TABLE inventory.lots (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid NOT NULL,  -- referencia blanda a core.stores
  product_id  uuid NOT NULL,  -- referencia blanda a catalog.products
  location_id uuid NOT NULL REFERENCES inventory.locations (id) ON DELETE RESTRICT,
  batch_code  text,
  expiry_date date,
  qty         numeric(14,3) NOT NULL DEFAULT 0 CHECK (qty >= 0),
  unit_cost   numeric(12,4) NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
  received_at timestamptz NOT NULL DEFAULT now(),
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
COMMENT ON COLUMN inventory.lots.expiry_date IS
  'Origen del evento lot.expiring_soon. NULL = producto no perecedero o lote sin caducidad.';

CREATE INDEX lots_product_idx ON inventory.lots (product_id);
CREATE INDEX lots_location_idx ON inventory.lots (location_id);
CREATE INDEX lots_store_idx ON inventory.lots (store_id);
-- Índice parcial: solo interesa lo que aún queda por caducar.
CREATE INDEX lots_expiry_idx ON inventory.lots (expiry_date) WHERE qty > 0;
-- El mismo número de lote puede recibirse varias veces en la misma ubicación
-- (reposición de un lote ya existente), por lo que batch_code NO es único.
CREATE INDEX lots_batch_idx ON inventory.lots (product_id, batch_code);

-- ---------------------------------------------------------------------
-- Movimientos de stock (append-only): la fuente de verdad trazable
-- ---------------------------------------------------------------------
CREATE TABLE inventory.stock_movements (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid NOT NULL,  -- referencia blanda a core.stores
  product_id  uuid NOT NULL,  -- referencia blanda a catalog.products
  lot_id      uuid REFERENCES inventory.lots (id) ON DELETE RESTRICT,
  location_id uuid REFERENCES inventory.locations (id) ON DELETE RESTRICT,
  type        inventory.movement_type NOT NULL,
  qty         numeric(14,3) NOT NULL,
  unit_cost   numeric(12,4) NOT NULL DEFAULT 0,
  reason_code text,
  ref_type    text,   -- 'reception' | 'sale' | 'task' | 'seed' ...
  ref_id      uuid,   -- referencia blanda al documento que lo origina
  user_id     uuid,   -- referencia blanda a core.users
  note        text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT stock_movements_qty_not_zero CHECK (qty <> 0)
);
COMMENT ON TABLE inventory.stock_movements IS
  'Tabla append-only: solo INSERT. Nunca se corrige un movimiento: se inserta el contrario.';

CREATE INDEX stock_movements_product_idx ON inventory.stock_movements (product_id, created_at DESC);
CREATE INDEX stock_movements_location_idx ON inventory.stock_movements (location_id);
CREATE INDEX stock_movements_lot_idx ON inventory.stock_movements (lot_id);
CREATE INDEX stock_movements_ref_idx ON inventory.stock_movements (ref_type, ref_id);
CREATE INDEX stock_movements_created_idx ON inventory.stock_movements (created_at DESC);
CREATE INDEX stock_movements_user_idx ON inventory.stock_movements (user_id, created_at DESC);
CREATE INDEX stock_movements_type_idx ON inventory.stock_movements (store_id, type, created_at DESC);

-- ---------------------------------------------------------------------
-- Mermas
-- ---------------------------------------------------------------------
CREATE TABLE inventory.wastage (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid NOT NULL,  -- referencia blanda a core.stores
  product_id  uuid NOT NULL,  -- referencia blanda a catalog.products
  lot_id      uuid REFERENCES inventory.lots (id) ON DELETE RESTRICT,
  location_id uuid REFERENCES inventory.locations (id) ON DELETE RESTRICT,
  qty         numeric(14,3) NOT NULL CHECK (qty > 0),
  reason_code inventory.wastage_reason NOT NULL,
  cost_impact numeric(12,2) NOT NULL DEFAULT 0 CHECK (cost_impact >= 0),
  photo_url   text,
  user_id     uuid,  -- referencia blanda a core.users
  notes       text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE inventory.wastage IS
  'Toda merma se registra con motivo: sin motivo no hay KPI ni aprendizaje posible.';

CREATE INDEX wastage_product_idx ON inventory.wastage (product_id, created_at DESC);
CREATE INDEX wastage_reason_idx ON inventory.wastage (store_id, reason_code, created_at DESC);
CREATE INDEX wastage_created_idx ON inventory.wastage (created_at DESC);
CREATE INDEX wastage_lot_idx ON inventory.wastage (lot_id);

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_locations_updated_at
  BEFORE UPDATE ON inventory.locations
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_stock_updated_at
  BEFORE UPDATE ON inventory.stock
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_lots_updated_at
  BEFORE UPDATE ON inventory.lots
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_wastage_updated_at
  BEFORE UPDATE ON inventory.wastage
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();

-- ---------------------------------------------------------------------
-- Inmutabilidad
-- ---------------------------------------------------------------------
REVOKE UPDATE, DELETE ON inventory.stock_movements FROM PUBLIC;

CREATE TRIGGER trg_stock_movements_immutable
  BEFORE UPDATE OR DELETE ON inventory.stock_movements
  FOR EACH ROW EXECUTE FUNCTION util.forbid_mutation();
