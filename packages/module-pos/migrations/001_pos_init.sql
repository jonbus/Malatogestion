-- =====================================================================
-- POS · 001 · Cajas, sesiones, ventas y cobros
-- operator_id / product_id / store_id son referencias blandas: sin FK.
-- =====================================================================

CREATE TYPE pos.cash_session_status AS ENUM ('ABIERTA', 'CERRADA', 'ANULADA');
CREATE TYPE pos.sale_status AS ENUM ('COMPLETADA', 'ANULADA', 'PENDIENTE_SYNC');
CREATE TYPE pos.payment_method AS ENUM ('EFECTIVO', 'TARJETA', 'MIXTO', 'VALE', 'TRANSFERENCIA');

-- ---------------------------------------------------------------------
-- Cajas físicas
-- ---------------------------------------------------------------------
CREATE TABLE pos.registers (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid NOT NULL,  -- referencia blanda a core.stores
  code        text NOT NULL,
  name        text NOT NULL,
  location_id uuid,  -- referencia blanda a inventory.locations
  active      boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  deleted_at  timestamptz
);
CREATE UNIQUE INDEX registers_code_uq ON pos.registers (store_id, code) WHERE deleted_at IS NULL;

-- ---------------------------------------------------------------------
-- Sesiones de caja (turnos de cobro)
-- ---------------------------------------------------------------------
CREATE TABLE pos.cash_sessions (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id           uuid NOT NULL,  -- referencia blanda a core.stores
  register_id        uuid NOT NULL REFERENCES pos.registers (id) ON DELETE RESTRICT,
  status             pos.cash_session_status NOT NULL DEFAULT 'ABIERTA',
  opened_by          uuid NOT NULL,  -- referencia blanda a core.users
  opened_at          timestamptz NOT NULL DEFAULT now(),
  closed_by          uuid,  -- referencia blanda a core.users
  closed_at          timestamptz,
  opening_float      numeric(12,2) NOT NULL DEFAULT 0 CHECK (opening_float >= 0),
  expected_cash      numeric(12,2) CHECK (expected_cash IS NULL OR expected_cash >= 0),
  counted_cash       numeric(12,2) CHECK (counted_cash IS NULL OR counted_cash >= 0),
  difference         numeric(12,2),
  discrepancy_reason text,
  notes              text,
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT cash_sessions_closed_consistency
    CHECK (status <> 'CERRADA' OR (closed_at IS NOT NULL AND counted_cash IS NOT NULL))
);
COMMENT ON COLUMN pos.cash_sessions.difference IS
  'counted_cash - expected_cash. Un descuadre superior al umbral dispara cash_session.discrepancy.';

-- Índice único parcial: impide dos sesiones ABIERTA simultáneas en la misma caja.
CREATE UNIQUE INDEX cash_sessions_one_open_uq ON pos.cash_sessions (register_id) WHERE status = 'ABIERTA';
CREATE INDEX cash_sessions_register_idx ON pos.cash_sessions (register_id, opened_at DESC);
CREATE INDEX cash_sessions_store_idx ON pos.cash_sessions (store_id, opened_at DESC);
CREATE INDEX cash_sessions_operator_idx ON pos.cash_sessions (opened_by, opened_at DESC);
CREATE INDEX cash_sessions_status_idx ON pos.cash_sessions (store_id, status);

-- ---------------------------------------------------------------------
-- Ventas
-- ---------------------------------------------------------------------
CREATE TABLE pos.sales (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id         uuid NOT NULL,  -- referencia blanda a core.stores
  cash_session_id  uuid REFERENCES pos.cash_sessions (id) ON DELETE RESTRICT,
  register_id      uuid NOT NULL REFERENCES pos.registers (id) ON DELETE RESTRICT,
  ticket_number    text NOT NULL,
  status           pos.sale_status NOT NULL DEFAULT 'COMPLETADA',
  subtotal         numeric(12,2) NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
  discount_total   numeric(12,2) NOT NULL DEFAULT 0 CHECK (discount_total >= 0),
  tax_total        numeric(12,2) NOT NULL DEFAULT 0 CHECK (tax_total >= 0),
  total            numeric(12,2) NOT NULL DEFAULT 0 CHECK (total >= 0),
  operator_id      uuid NOT NULL,  -- referencia blanda a core.users
  sold_at          timestamptz NOT NULL DEFAULT now(),
  offline_sync_id  uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  synced_at        timestamptz,
  refund_of_sale_id uuid REFERENCES pos.sales (id) ON DELETE SET NULL,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);
COMMENT ON COLUMN pos.sales.offline_sync_id IS
  'UUID generado en el cliente. Garantiza idempotencia al sincronizar cobros hechos sin conexión.';

-- La numeración de ticket es POR CAJA: dos cajas distintas pueden emitir el mismo
-- número, sobre todo al reconciliar ventas hechas sin conexión. Solo es único
-- dentro de su propia caja. La idempotencia de la sincronización la da offline_sync_id.
CREATE UNIQUE INDEX sales_ticket_uq ON pos.sales (store_id, register_id, ticket_number);
CREATE INDEX sales_session_idx ON pos.sales (cash_session_id);
CREATE INDEX sales_register_idx ON pos.sales (register_id);
CREATE INDEX sales_sold_at_idx ON pos.sales (store_id, sold_at DESC);
CREATE INDEX sales_operator_idx ON pos.sales (operator_id, sold_at DESC);
CREATE INDEX sales_refund_idx ON pos.sales (refund_of_sale_id) WHERE refund_of_sale_id IS NOT NULL;
CREATE INDEX sales_pending_sync_idx ON pos.sales (store_id, sold_at) WHERE status = 'PENDIENTE_SYNC';

-- ---------------------------------------------------------------------
-- Líneas de venta (inmutables una vez cobrada la venta)
-- ---------------------------------------------------------------------
CREATE TABLE pos.sale_lines (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_id     uuid NOT NULL REFERENCES pos.sales (id) ON DELETE CASCADE,
  line_no     integer NOT NULL CHECK (line_no > 0),
  -- NULL = LINEA LIBRE: venta de un producto que la app no conoce (pack, articulo
  -- de temporada, producto aun sin dar de alta). La app no integra todo el catalogo
  -- de la tienda, asi que en caja hay que poder cobrar lo que no esta en el sistema.
  -- El CHECK de abajo obliga a que, si no hay producto, haya al menos descripcion.
  product_id  uuid,  -- referencia blanda a catalog.products
  description text,
  qty         numeric(14,3) NOT NULL CHECK (qty > 0),
  unit_price  numeric(12,4) NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
  discount    numeric(12,2) NOT NULL DEFAULT 0 CHECK (discount >= 0),
  tax_rate    numeric(5,2) NOT NULL DEFAULT 0 CHECK (tax_rate >= 0),
  line_total  numeric(12,2) NOT NULL DEFAULT 0 CHECK (line_total >= 0),
  created_at  timestamptz NOT NULL DEFAULT now(),
  -- O hay producto del catalogo, o hay descripcion libre. Nunca ninguno de los dos.
  CONSTRAINT sale_lines_producto_o_descripcion
    CHECK (product_id IS NOT NULL OR description IS NOT NULL)
);
CREATE UNIQUE INDEX sale_lines_no_uq ON pos.sale_lines (sale_id, line_no);
CREATE INDEX sale_lines_product_idx ON pos.sale_lines (product_id, created_at DESC);

-- ---------------------------------------------------------------------
-- Cobros (una venta puede tener varios: pago mixto)
-- ---------------------------------------------------------------------
CREATE TABLE pos.payments (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_id      uuid NOT NULL REFERENCES pos.sales (id) ON DELETE CASCADE,
  method       pos.payment_method NOT NULL,
  amount       numeric(12,2) NOT NULL CHECK (amount <> 0),
  change_given numeric(12,2) NOT NULL DEFAULT 0 CHECK (change_given >= 0),
  card_last4   char(4),
  auth_code    text,
  created_at   timestamptz NOT NULL DEFAULT now()
);
-- Varios cobros del mismo método en una venta son legítimos (pago dividido en
-- dos pasadas de tarjeta, dos vales, etc.). Por eso NO hay unicidad (sale_id, method).
-- No hay índice por (sale_id) suelto: payments_sale_method_idx ya lo cubre
-- por prefijo izquierdo, y pos.payments es una tabla de alta escritura.
CREATE INDEX payments_sale_method_idx ON pos.payments (sale_id, method);
CREATE INDEX payments_method_idx ON pos.payments (method, created_at DESC);

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_registers_updated_at
  BEFORE UPDATE ON pos.registers
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_cash_sessions_updated_at
  BEFORE UPDATE ON pos.cash_sessions
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_sales_updated_at
  BEFORE UPDATE ON pos.sales
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
