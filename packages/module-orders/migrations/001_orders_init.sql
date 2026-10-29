-- =====================================================================
-- ORDERS · 001 · Pedidos a proveedor y recepciones de mercancía
-- supplier_id / product_id / generated_by_rule_id son referencias blandas.
-- =====================================================================

CREATE TYPE orders.purchase_order_status AS ENUM ('BORRADOR', 'ENVIADO', 'PARCIAL', 'RECIBIDO', 'CANCELADO');
CREATE TYPE orders.order_line_status AS ENUM ('PENDIENTE', 'PARCIAL', 'COMPLETA', 'CANCELADA');
CREATE TYPE orders.reception_status AS ENUM ('BORRADOR', 'CONFIRMADA', 'ANULADA');

-- ---------------------------------------------------------------------
-- Pedidos a proveedor
-- ---------------------------------------------------------------------
CREATE TABLE orders.purchase_orders (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id             uuid NOT NULL,  -- referencia blanda a core.stores
  code                 text NOT NULL,
  supplier_id          uuid NOT NULL,  -- referencia blanda a catalog.suppliers
  status               orders.purchase_order_status NOT NULL DEFAULT 'BORRADOR',
  expected_date        date,
  subtotal             numeric(12,2) NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
  tax_total            numeric(12,2) NOT NULL DEFAULT 0 CHECK (tax_total >= 0),
  total                numeric(12,2) NOT NULL DEFAULT 0 CHECK (total >= 0),
  notes                text,
  generated_by_rule_id uuid,  -- referencia blanda a rules.rules: responde "por qué se pidió esto"
  created_by           uuid,  -- referencia blanda a core.users (NULL = generado por el motor)
  approved_by          uuid,  -- referencia blanda a core.users
  approved_at          timestamptz,
  sent_at              timestamptz,
  created_at           timestamptz NOT NULL DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now(),
  deleted_at           timestamptz,
  CONSTRAINT purchase_orders_approved_consistency
    CHECK (approved_at IS NULL OR approved_by IS NOT NULL)
);
COMMENT ON COLUMN orders.purchase_orders.generated_by_rule_id IS
  'Trazabilidad del motor de reglas: permite auditar por que se genero un pedido automatico.';

CREATE UNIQUE INDEX purchase_orders_code_uq ON orders.purchase_orders (store_id, code) WHERE deleted_at IS NULL;
CREATE INDEX purchase_orders_supplier_idx ON orders.purchase_orders (supplier_id, status);
CREATE INDEX purchase_orders_status_idx ON orders.purchase_orders (store_id, status, expected_date);
CREATE INDEX purchase_orders_created_idx ON orders.purchase_orders (store_id, created_at DESC);
CREATE INDEX purchase_orders_rule_idx
  ON orders.purchase_orders (generated_by_rule_id) WHERE generated_by_rule_id IS NOT NULL;

-- ---------------------------------------------------------------------
-- Líneas de pedido
-- ---------------------------------------------------------------------
CREATE TABLE orders.purchase_order_lines (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id      uuid NOT NULL REFERENCES orders.purchase_orders (id) ON DELETE CASCADE,
  line_no       integer NOT NULL CHECK (line_no > 0),
  product_id    uuid NOT NULL,  -- referencia blanda a catalog.products
  qty_ordered   numeric(14,3) NOT NULL CHECK (qty_ordered > 0),
  qty_received  numeric(14,3) NOT NULL DEFAULT 0 CHECK (qty_received >= 0),
  unit_cost     numeric(12,4) NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
  line_total    numeric(12,2) NOT NULL DEFAULT 0 CHECK (line_total >= 0),
  line_status   orders.order_line_status NOT NULL DEFAULT 'PENDIENTE',
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX purchase_order_lines_no_uq ON orders.purchase_order_lines (order_id, line_no);
CREATE INDEX purchase_order_lines_product_idx ON orders.purchase_order_lines (product_id);
CREATE INDEX purchase_order_lines_status_idx ON orders.purchase_order_lines (order_id, line_status);

-- ---------------------------------------------------------------------
-- Recepciones (pueden existir sin pedido previo: order_id NULL)
-- ---------------------------------------------------------------------
CREATE TABLE orders.receptions (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id         uuid NOT NULL,  -- referencia blanda a core.stores
  order_id         uuid REFERENCES orders.purchase_orders (id) ON DELETE SET NULL,
  supplier_id      uuid NOT NULL,  -- referencia blanda a catalog.suppliers
  delivery_note    text,
  status           orders.reception_status NOT NULL DEFAULT 'BORRADOR',
  received_by      uuid,  -- referencia blanda a core.users
  received_at      timestamptz,
  total            numeric(12,2) NOT NULL DEFAULT 0 CHECK (total >= 0),
  incidences_count integer NOT NULL DEFAULT 0 CHECK (incidences_count >= 0),
  notes            text,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT receptions_received_consistency
    CHECK (status <> 'CONFIRMADA' OR received_at IS NOT NULL)
);
CREATE INDEX receptions_order_idx ON orders.receptions (order_id);
CREATE INDEX receptions_supplier_idx ON orders.receptions (supplier_id, received_at DESC);
CREATE INDEX receptions_store_idx ON orders.receptions (store_id, received_at DESC);
CREATE INDEX receptions_status_idx ON orders.receptions (store_id, status);

-- ---------------------------------------------------------------------
-- Líneas de recepción (cantidad real, lote y caducidad declarados)
-- ---------------------------------------------------------------------
CREATE TABLE orders.reception_lines (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reception_id uuid NOT NULL REFERENCES orders.receptions (id) ON DELETE CASCADE,
  po_line_id   uuid REFERENCES orders.purchase_order_lines (id) ON DELETE SET NULL,
  product_id   uuid NOT NULL,  -- referencia blanda a catalog.products
  qty          numeric(14,3) NOT NULL CHECK (qty >= 0),
  unit_cost    numeric(12,4) NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
  lot_code     text,
  expiry_date  date,
  incidences   jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT reception_lines_incidences_array CHECK (jsonb_typeof(incidences) = 'array')
);
COMMENT ON COLUMN orders.reception_lines.incidences IS
  'Lista JSONB: falta cantidad, producto equivocado, packaging dañado, precio distinto.';

CREATE INDEX reception_lines_reception_idx ON orders.reception_lines (reception_id);
CREATE INDEX reception_lines_product_idx ON orders.reception_lines (product_id);
CREATE INDEX reception_lines_po_line_idx ON orders.reception_lines (po_line_id);
CREATE INDEX reception_lines_expiry_idx ON orders.reception_lines (expiry_date) WHERE expiry_date IS NOT NULL;
CREATE INDEX reception_lines_incidences_gin ON orders.reception_lines USING gin (incidences jsonb_path_ops);

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_purchase_orders_updated_at
  BEFORE UPDATE ON orders.purchase_orders
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_purchase_order_lines_updated_at
  BEFORE UPDATE ON orders.purchase_order_lines
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_receptions_updated_at
  BEFORE UPDATE ON orders.receptions
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_reception_lines_updated_at
  BEFORE UPDATE ON orders.reception_lines
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
