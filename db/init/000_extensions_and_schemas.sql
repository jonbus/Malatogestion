-- =====================================================================
-- 000 · Extensiones y esquemas base
-- Ejecutar sobre una base de datos VACÍA, antes de cualquier migración.
-- =====================================================================

-- Extensiones requeridas por el diseño (Fase 1 / Fase 2)
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;    -- emails y códigos sin distinguir mayúsculas
CREATE EXTENSION IF NOT EXISTS ltree;     -- jerarquía de categorías

-- Funciones de trigger compartidas
CREATE SCHEMA IF NOT EXISTS util;

-- Un esquema por módulo. Ningún módulo escribe fuera del suyo.
CREATE SCHEMA IF NOT EXISTS core;       -- identidad, RBAC, auditoría, outbox, configuración
CREATE SCHEMA IF NOT EXISTS catalog;    -- productos, categorías, proveedores
CREATE SCHEMA IF NOT EXISTS inventory;  -- stock, lotes, movimientos, mermas
CREATE SCHEMA IF NOT EXISTS orders;     -- pedidos a proveedor y recepciones
CREATE SCHEMA IF NOT EXISTS tasks;      -- motor de tareas y tablero kanban
CREATE SCHEMA IF NOT EXISTS pos;        -- caja, ventas y cobros
CREATE SCHEMA IF NOT EXISTS notify;     -- notificaciones y suscripciones
CREATE SCHEMA IF NOT EXISTS analytics;  -- KPIs y snapshots

COMMENT ON SCHEMA util      IS 'Funciones de trigger compartidas. Sin datos de negocio.';
COMMENT ON SCHEMA core      IS 'CORE: identidad, RBAC, auditoría, outbox y configuración.';
COMMENT ON SCHEMA catalog   IS 'Catálogo: categorías, productos y proveedores.';
COMMENT ON SCHEMA inventory IS 'Inventario: ubicaciones, stock, lotes, movimientos y mermas.';
COMMENT ON SCHEMA orders    IS 'Compras: pedidos a proveedor y recepciones.';
COMMENT ON SCHEMA tasks     IS 'Tareas: plantillas, tareas y tablero.';
COMMENT ON SCHEMA pos       IS 'TPV: cajas, sesiones, ventas y cobros.';
COMMENT ON SCHEMA notify    IS 'Notificaciones: avisos y suscripciones por usuario.';
COMMENT ON SCHEMA analytics IS 'Analítica: snapshots de KPI para dashboards.';
