-- =====================================================================
-- ANALYTICS · 001 · Snapshots de KPI para los dashboards adaptativos
-- No escribe en ningún otro módulo: consume eventos del bus y proyecta aquí.
-- =====================================================================

CREATE TABLE analytics.kpi_snapshots (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  store_id    uuid NOT NULL,  -- referencia blanda a core.stores
  kpi_code    text NOT NULL,  -- p.ej. sales.total, margin.percent, wastage.cost
  date        date NOT NULL,
  period      text NOT NULL DEFAULT 'DAY',  -- DAY | WEEK | MONTH
  value       numeric(16,4) NOT NULL DEFAULT 0,
  dimensions  jsonb NOT NULL DEFAULT '{}'::jsonb,
  computed_at timestamptz NOT NULL DEFAULT now(),
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT kpi_snapshots_dimensions_object CHECK (jsonb_typeof(dimensions) = 'object'),
  CONSTRAINT kpi_snapshots_period_values CHECK (period IN ('DAY', 'WEEK', 'MONTH'))
);
COMMENT ON TABLE analytics.kpi_snapshots IS
  'Serie de KPI por tienda, fecha, periodo y dimensiones. Reprocesable desde core.outbox_events.';
COMMENT ON COLUMN analytics.kpi_snapshots.dimensions IS
  'Desglose del KPI: {"category":"lacteos"}, {"operatorId":"..."}, {"canal":"TIENDA"}.';

CREATE UNIQUE INDEX kpi_snapshots_uq
  ON analytics.kpi_snapshots (store_id, kpi_code, date, period, dimensions);
CREATE INDEX kpi_snapshots_series_idx ON analytics.kpi_snapshots (store_id, kpi_code, date DESC);
CREATE INDEX kpi_snapshots_period_idx ON analytics.kpi_snapshots (store_id, period, date DESC);
CREATE INDEX kpi_snapshots_dimensions_gin ON analytics.kpi_snapshots USING gin (dimensions jsonb_path_ops);

-- ---------------------------------------------------------------------
-- Triggers updated_at
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_kpi_snapshots_updated_at
  BEFORE UPDATE ON analytics.kpi_snapshots
  FOR EACH ROW EXECUTE FUNCTION util.set_updated_at();
