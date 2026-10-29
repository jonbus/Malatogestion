-- =====================================================================
-- CATALOG · 001 · Categorías, proveedores, productos y su relación
-- Referencias externas (store_id, core.users) son blandas: sin FK.
-- =====================================================================

CREATE TYPE catalog.product_unit AS ENUM ('UD', 'KG');

-- ---------------------------------------------------------------------
-- Categorías (jerarquía con ltree; los labels solo admiten [A-Za-z0-9_])
-- ---------------------------------------------------------------------
CREATE TABLE catalog.categories (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id   uuid NOT NULL,  -- referencia blanda a core.stores
  parent_id  uuid REFERENCES catalog.categories (id) ON DELETE RESTRICT,
  name       text NOT NULL,
  slug       text NOT NULL,
  path       ltree NOT NULL,
  sort_order integer NOT NULL DEFAULT 0,
  active     boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz
);
COMMENT ON COLUMN catalog.categories.path IS
  'Ruta ltree, p.ej. lacteos.leche. Permite subárboles con el operador <@ en una sola consulta.';

CREATE UNIQUE INDEX categories_slug_uq ON catalog.categories (store_id, slug) WHERE deleted_at IS NULL;
CREATE INDEX categories_path_gist ON catalog.categories USING gist (path);
CREATE INDEX categories_parent_idx ON catalog.categories (parent_id);
CREATE INDEX categories_store_sort_idx ON catalog.categories (store_id, sort_order) WHERE deleted_at IS NULL;

-- ---------------------------------------------------------------------
-- Proveedores
-- ---------------------------------------------------------------------
CREATE TABLE catalog.suppliers (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id        uuid NOT NULL,  -- referencia blanda a core.stores
  code            text NOT NULL,
  name            text NOT NULL,
  contact         jsonb NOT NULL DEFAULT '{}'::jsonb,
  lead_time_days  integer NOT NULL DEFAULT 1 CHECK (lead_time_days >= 0),
  order_weekdays  integer[] NOT NULL DEFAULT '{}',  -- ISO: 1=lunes ... 7=domingo
  cutoff_time     time,
  min_order_value numeric(10,2) NOT NULL DEFAULT 0 CHECK (min_order_value >= 0),
  payment_terms   text,
  email           citext,
  phone           text,
  active          boolean NOT NULL DEFAULT true,
  notes           text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz,
  CONSTRAINT suppliers_contact_object CHECK (jsonb_typeof(contact) = 'object'),
  CONSTRAINT suppliers_weekdays_range CHECK (
    order_weekdays <@ ARRAY[1,2,3,4,5,6,7]::integer[]
  )
);
COMMENT ON COLUMN catalog.suppliers.order_weekdays IS
  'Días ISO en que se puede pedir. El motor de reglas lo usa para decidir cuándo generar borradores de pedido.';

CREATE UNIQUE INDEX suppliers_code_uq ON catalog.suppliers (store_id, code) WHERE deleted_at IS NULL;
CREATE INDEX suppliers_weekdays_gin ON catalog.suppliers USING gin (order_weekdays);
CREATE INDEX suppliers_contact_gin ON catalog.suppliers USING gin (contact jsonb_path_ops);
CREATE INDEX suppliers_active_idx ON catalog.suppliers (store_id) WHERE active AND deleted_at IS NULL;

-- ---------------------------------------------------------------------
-- Productos
-- ---------------------------------------------------------------------
CREATE TABLE catalog.products (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id        uuid NOT NULL,  -- referencia blanda a core.stores
  sku             text NOT NULL,
  ean             char(13),
  name            text NOT NULL,
  category_id     uuid REFERENCES catalog.categories (id) ON DELETE RESTRICT,
  unit            catalog.product_unit NOT NULL DEFAULT 'UD',
  is_weighted     boolean NOT NULL DEFAULT false,
  is_perishable   boolean NOT NULL DEFAULT false,
  tax_rate        numeric(5,2) NOT NULL DEFAULT 10.00 CHECK (tax_rate >= 0),
  cost            numeric(12,4) NOT NULL DEFAULT 0 CHECK (cost >= 0),
  price           numeric(12,4) NOT NULL DEFAULT 0 CHECK (price >= 0),
  min_stock       numeric(12,3) NOT NULL DEFAULT 0 CHECK (min_stock >= 0),
  target_stock    numeric(12,3) NOT NULL DEFAULT 0 CHECK (target_stock >= 0),
  shelf_life_days integer CHECK (shelf_life_days IS NULL OR shelf_life_days >= 0),
  attributes      jsonb NOT NULL DEFAULT '{}'::jsonb,
  active          boolean NOT NULL DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz,
  CONSTRAINT products_ean_format CHECK (ean IS NULL OR ean ~ '^[0-9]{13}$'),
  CONSTRAINT products_attributes_object CHECK (jsonb_typeof(attributes) = 'object'),
  CONSTRAINT products_target_gte_min CHECK (target_stock >= min_stock)
);
COMMENT ON COLUMN catalog.products.attributes IS
  'Atributos que el negocio define (marca, formato, alérgenos, conservación). JSONB para no migrar el esquema.';
COMMENT ON COLUMN catalog.products.min_stock IS
  'Umbral de rotura. inventory emite stock.below_minimum al cruzarlo y el motor de reglas decide.';

CREATE UNIQUE INDEX products_sku_uq ON catalog.products (store_id, sku) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX products_ean_uq ON catalog.products (store_id, ean) WHERE ean IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX products_category_idx ON catalog.products (category_id);
CREATE INDEX products_store_active_idx ON catalog.products (store_id, active) WHERE deleted_at IS NULL;
CREATE INDEX products_perishable_idx ON catalog.products (store_id) WHERE is_perishable AND deleted_at IS NULL;
CREATE INDEX products_attributes_gin ON catalog.products USING gin (attributes jsonb_path_ops);

-- ---------------------------------------------------------------------
-- Multi-proveedor por producto (uno marcado como preferente)
-- ---------------------------------------------------------------------
CREATE TABLE catalog.product_suppliers (
  product_id      uuid NOT NULL REFERENCES catalog.products (id) ON DELETE CASCADE,
  supplier_id     uuid NOT NULL REFERENCES catalog.suppliers (id) ON DELETE CASCADE,
  supplier_sku    text,
  pack_size       numeric(12,3) NOT NULL DEFAULT 1 CHECK (pack_size > 0),
  cost            numeric(12,4) NOT NULL DEFAULT 0 CHECK (cost >= 0),
  is_preferred    boolean NOT NULL DEFAULT false,
  lead_time_days  integer CHECK (lead_time_days IS NULL OR lead_time_days >= 0),
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (product_id, supplier_id)
);
CREATE INDEX product_suppliers_supplier_idx ON catalog.product_suppliers (supplier_id);
CREATE UNIQUE INDEX product_suppliers_preferred_uq
  ON catalog.product_suppliers (product_id) WHERE is_preferred;

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_categories_updated_at
  BEFORE UPDATE ON catalog.categories
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_suppliers_updated_at
  BEFORE UPDATE ON catalog.suppliers
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_products_updated_at
  BEFORE UPDATE ON catalog.products
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
CREATE TRIGGER trg_product_suppliers_updated_at
  BEFORE UPDATE ON catalog.product_suppliers
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
