-- =====================================================================
-- SEED · 001 · Tienda de demostración (alimentación, España)
-- Idempotente: puede ejecutarse varias veces sin duplicar datos.
-- Ejecutar DESPUÉS de db/init/* + todas las migraciones de módulo.
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- Resolutor de ids por clave lógica (evita hardcodear uuid)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS _seed_ids;
CREATE TEMP TABLE _seed_ids (key text PRIMARY KEY, id uuid NOT NULL) ON COMMIT DROP;

CREATE OR REPLACE FUNCTION pg_temp.seed_id(p_key text)
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
  SELECT id FROM pg_temp._seed_ids WHERE key = p_key;
$$;

-- =====================================================================
-- CORE · tienda, roles, permisos y usuarios
-- =====================================================================
INSERT INTO core.stores (code, name, address, timezone, currency)
VALUES ('TIENDA-01', 'Malato Alimentación',
        '{"calle":"Calle Mayor 14","ciudad":"Valencia","cp":"46001","pais":"ES","telefono":"+34963000000"}'::jsonb,
        'Europe/Madrid', 'EUR')
ON CONFLICT DO NOTHING;

INSERT INTO _seed_ids (key, id)
SELECT 'store', id FROM core.stores WHERE code = 'TIENDA-01'
ON CONFLICT (key) DO UPDATE SET id = EXCLUDED.id;

-- El nivel hace los roles JERARQUICOS, no excluyentes: una persona puede tomar
-- cualquier tarea cuyo required_role tenga nivel menor o igual al suyo.
-- GERENCIA 30 > COORDINADORA 20 > OPERADORA 10.
INSERT INTO core.roles (code, name, description, is_system, level) VALUES
  ('GERENCIA',     'Gerencia',                    'Acceso total: reglas de negocio, precios, pedidos y KPIs.', true, 30),
  ('COORDINADORA', 'Coordinación de operaciones', 'Encargada: dueña del catálogo, reparte, valida y además repone y cobra.', true, 20),
  ('OPERADORA',    'Operadora de sala',           'Rol ejecutivo: caja, reposición y tareas asignadas.',        true, 10)
ON CONFLICT DO NOTHING;

INSERT INTO core.permissions (code, module, description) VALUES
  ('core.users.read',              'core',      'Ver usuarios'),
  ('core.users.manage',            'core',      'Crear y editar usuarios'),
  ('core.roles.manage',            'core',      'Gestionar roles y permisos'),
  ('core.settings.manage',         'core',      'Editar la configuración de la tienda'),
  ('core.audit.read',              'core',      'Consultar la auditoría'),
  ('catalog.products.read',        'catalog',   'Ver el catálogo de productos'),
  ('catalog.products.manage',      'catalog',   'Crear y editar productos y categorías'),
  ('catalog.suppliers.manage',     'catalog',   'Gestionar proveedores'),
  ('catalog.prices.manage',        'catalog',   'Modificar precios y costes'),
  ('inventory.read',               'inventory', 'Consultar stock, lotes y caducidades'),
  ('inventory.adjust',             'inventory', 'Ajustar stock y traspasar entre ubicaciones'),
  ('inventory.wastage.register',   'inventory', 'Registrar mermas'),
  ('inventory.lots.manage',        'inventory', 'Gestionar lotes y caducidades'),
  ('orders.read',                  'orders',    'Ver pedidos y recepciones'),
  ('orders.create',                'orders',    'Crear borradores de pedido'),
  ('orders.approve',               'orders',    'Aprobar pedidos a proveedor'),
  ('orders.send',                  'orders',    'Enviar pedidos al proveedor'),
  ('orders.receive',               'orders',    'Registrar recepciones de mercancía'),
  ('tasks.read',                   'tasks',     'Ver tareas propias y del equipo'),
  ('tasks.create',                 'tasks',     'Crear tareas manuales'),
  ('tasks.assign',                 'tasks',     'Asignar tareas'),
  ('tasks.reassign',               'tasks',     'Redistribuir tareas en tiempo real'),
  ('tasks.complete',               'tasks',     'Completar tareas asignadas'),
  ('tasks.templates.manage',       'tasks',     'Gestionar plantillas de tarea'),
  ('rules.read',                   'tasks',     'Ver el motor de reglas'),
  ('rules.manage',                 'tasks',     'Crear, editar y activar reglas'),
  ('rules.simulate',               'tasks',     'Simular reglas antes de activarlas'),
  ('rules.override',               'tasks',     'Forzar la asignación de una regla para un día'),
  ('pos.open_session',             'pos',       'Abrir sesión de caja'),
  ('pos.close_session',            'pos',       'Cerrar sesión de caja y arquear'),
  ('pos.sell',                     'pos',       'Cobrar en caja'),
  ('pos.refund',                   'pos',       'Anular o devolver una venta'),
  ('pos.sessions.read',            'pos',       'Consultar sesiones y descuadres de caja'),
  ('notify.read',                  'notify',    'Ver notificaciones'),
  ('notify.manage',                'notify',    'Configurar alertas y suscripciones'),
  ('analytics.dashboard.gerencia', 'analytics', 'Dashboard ejecutivo'),
  ('analytics.dashboard.operaciones', 'analytics', 'Dashboard de operaciones'),
  ('analytics.kpi.read',           'analytics', 'Consultar KPIs'),
  ('analytics.margin.read',        'analytics', 'Consultar márgenes y costes'),
  ('analytics.export',             'analytics', 'Exportar informes')
ON CONFLICT DO NOTHING;

-- Gerencia tiene acceso a todo.
INSERT INTO core.role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM core.roles r
CROSS JOIN core.permissions p
WHERE r.code = 'GERENCIA'
ON CONFLICT DO NOTHING;

-- Coordinación: ENCARGADAS. El rol es JERÁRQUICO, no disjunto: incluye TODO lo que
-- puede hacer una operadora (en una tienda con 2 operadoras y 91 h semanales de
-- apertura, quien coordina también repone y cobra) más sus propias facultades.
-- Es la DUEÑA DEL CATÁLOGO, de ahí 'catalog.products.manage'.
INSERT INTO core.role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM core.roles r
JOIN core.permissions p ON p.code = ANY (ARRAY[
  -- todo lo de OPERADORA (ver más abajo): los roles son jerárquicos
  'catalog.products.read',
  'inventory.read', 'inventory.wastage.register',
  'tasks.read', 'tasks.complete',
  'pos.open_session', 'pos.close_session', 'pos.sell',
  'notify.read',
  -- facultades propias de coordinación
  'catalog.products.manage',
  'inventory.adjust', 'inventory.lots.manage',
  'orders.read', 'orders.create', 'orders.send', 'orders.receive',
  'tasks.create', 'tasks.assign', 'tasks.reassign',
  'rules.read', 'rules.simulate', 'rules.override',
  'pos.sessions.read',
  'notify.manage',
  'analytics.dashboard.operaciones', 'analytics.kpi.read'
])
WHERE r.code = 'COORDINADORA'
ON CONFLICT DO NOTHING;

-- Operadoras: ejecución y cobro.
INSERT INTO core.role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM core.roles r
JOIN core.permissions p ON p.code = ANY (ARRAY[
  'catalog.products.read',
  'inventory.read', 'inventory.wastage.register',
  'tasks.read', 'tasks.complete',
  'pos.open_session', 'pos.close_session', 'pos.sell',
  'notify.read'
])
WHERE r.code = 'OPERADORA'
ON CONFLICT DO NOTHING;

-- Plantilla real: 6 personas = 1 Gerencia + 3 Coordinadoras + 2 Operadoras.
-- Tres coordinadoras no son un lujo: la tienda abre 91 h/semana y dos personas a
-- jornada completa son 80 h, así que con dos es imposible cubrir todos los turnos.
-- ATENCIÓN: el hash del PIN es un PLACEHOLDER simbólico.
-- La aplicación debe generar el hash real (argon2id o bcrypt) en el alta
-- de usuario y volver a sembrarlo; el valor de abajo NO permite iniciar sesión.
INSERT INTO core.users (store_id, email, full_name, role_id, pin_caja, phone)
SELECT pg_temp.seed_id('store'), v.email::citext, v.full_name, r.id, v.pin_hash, v.phone
FROM (VALUES
  ('gerencia@malato.es',      'Marta Ferrer',   'GERENCIA',     '$argon2id$SEED_PLACEHOLDER$gerencia-1234',     '+34600000001'),
  ('coordinacion1@malato.es', 'Lucía Sanchis',  'COORDINADORA', '$argon2id$SEED_PLACEHOLDER$coord1-2345',       '+34600000002'),
  ('coordinacion2@malato.es', 'Nuria Blasco',   'COORDINADORA', '$argon2id$SEED_PLACEHOLDER$coord2-3456',       '+34600000003'),
  ('coordinacion3@malato.es', 'Rocío Beltrán',  'COORDINADORA', '$argon2id$SEED_PLACEHOLDER$coord3-6789',       '+34600000004'),
  ('sala1@malato.es',         'Ana Torres',     'OPERADORA',    '$argon2id$SEED_PLACEHOLDER$operadora1-4567',   '+34600000005'),
  ('sala2@malato.es',         'Paula Giner',    'OPERADORA',    '$argon2id$SEED_PLACEHOLDER$operadora2-5678',   '+34600000006')
) AS v(email, full_name, role_code, pin_hash, phone)
JOIN core.roles r ON r.code = v.role_code
ON CONFLICT DO NOTHING;

-- Excepción puntual sobre el rol: coordinación 1 puede aprobar pedidos.
INSERT INTO core.user_permissions (user_id, permission_id, granted)
SELECT u.id, p.id, true
FROM core.users u
JOIN core.permissions p ON p.code = 'orders.approve'
WHERE u.email = 'coordinacion1@malato.es'::citext
ON CONFLICT DO NOTHING;

INSERT INTO core.settings (store_id, key, module, value, description)
VALUES
  (pg_temp.seed_id('store'), 'pos.discrepancy_threshold_eur', 'pos', '{"threshold_eur": 5}'::jsonb,
   'Descuadre de caja a partir del cual se avisa a gerencia.'),
  (pg_temp.seed_id('store'), 'tasks.engine.enabled', 'tasks', '{"enabled": true}'::jsonb,
   'Interruptor de pánico del motor de tareas.')
ON CONFLICT DO NOTHING;

-- =====================================================================
-- CATALOG · categorías, proveedores y productos
-- =====================================================================
-- Categorías raíz
INSERT INTO catalog.categories (store_id, parent_id, name, slug, path, sort_order)
SELECT pg_temp.seed_id('store'), NULL, v.name, v.slug, v.path::ltree, v.sort
FROM (VALUES
  ('Lácteos',  'lacteos',  'lacteos',  10),
  ('Frescos',  'frescos',  'frescos',  20),
  ('Despensa', 'despensa', 'despensa', 30),
  ('Bebidas',  'bebidas',  'bebidas',  40)
) AS v(name, slug, path, sort)
ON CONFLICT DO NOTHING;

-- Categorías hijas (padre resuelto por su ruta ltree)
INSERT INTO catalog.categories (store_id, parent_id, name, slug, path, sort_order)
SELECT pg_temp.seed_id('store'), padre.id, v.name, v.slug, v.path::ltree, v.sort
FROM (VALUES
  ('Leche y nata',      'lacteos-leche',    'lacteos.leche',            11, 'lacteos'),
  ('Yogures y postres', 'lacteos-yogures',  'lacteos.yogures',          12, 'lacteos'),
  ('Frutas y verduras', 'frescos-frutas',   'frescos.frutas_verduras',  21, 'frescos'),
  ('Carnicería',        'frescos-carniceria','frescos.carniceria',      22, 'frescos')
) AS v(name, slug, path, sort, parent_path)
JOIN catalog.categories padre
  ON padre.path = v.parent_path::ltree
 AND padre.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

INSERT INTO catalog.suppliers (store_id, code, name, contact, lead_time_days, order_weekdays, cutoff_time, min_order_value, payment_terms, email, phone)
SELECT pg_temp.seed_id('store'), v.code, v.name, v.contact, v.lead, v.days, v.cutoff, v.min_order, v.terms, v.email::citext, v.phone
FROM (VALUES
  ('LACT-01', 'Lácteos del Turia S.L.',
   '{"persona":"José Ramón Císcar","direccion":"Polígono Fuente del Jarro, Paterna (Valencia)"}'::jsonb,
   2, '{1,3,5}'::integer[], '14:00'::time, 150.00, 'Transferencia 30 días', 'pedidos@lacteosdelturia.es', '+34961110001'),
  ('FRUT-01', 'Frutas y Verduras Hermanos Peiró',
   '{"persona":"Salvador Peiró","direccion":"Mercavalencia, nave 42"}'::jsonb,
   1, '{1,2,3,4,5,6}'::integer[], '22:00'::time, 200.00, 'Contado semanal', 'pedidos@frutaspeiro.es', '+34961110002'),
  ('CARN-01', 'Cárnicas Serra e Hijos',
   '{"persona":"Vicente Serra","direccion":"Polígono El Oliveral, Ribarroja (Valencia)"}'::jsonb,
   2, '{2,4}'::integer[], '12:00'::time, 250.00, 'Transferencia 15 días', 'pedidos@carnicasserra.es', '+34961110003'),
  ('DIST-01', 'Distribuciones Mediterráneo S.A.',
   '{"persona":"Elena Ferrer","direccion":"Avda. del Puerto 210, Valencia"}'::jsonb,
   3, '{1,4}'::integer[], '17:00'::time, 300.00, 'Transferencia 45 días', 'compras@distmediterraneo.es', '+34961110004')
) AS v(code, name, contact, lead, days, cutoff, min_order, terms, email, phone)
ON CONFLICT DO NOTHING;

-- ~30 productos españoles. EAN-13 con prefijo 84 (España) y dígito de control correcto.
-- IVA aplicado: 4% básicos, 10% alimentación general, 21% alcohol.
INSERT INTO catalog.products (store_id, sku, ean, name, category_id, unit, is_weighted, is_perishable,
                              tax_rate, cost, price, min_stock, target_stock, shelf_life_days, attributes)
SELECT pg_temp.seed_id('store'), v.sku, v.ean, v.name, c.id, v.unit::catalog.product_unit,
       v.weighted, v.perishable, v.tax, v.cost, v.price, v.min_stock, v.target_stock, v.shelf_life, v.attrs
FROM (VALUES
  ('LAC-001','8412345000010','Leche entera UHT Pascual 1 L',        'lacteos.leche','UD',false,false, 4.00,0.78, 1.05, 48,120,180,'{"marca":"Pascual","formato":"1 L","conservacion":"Ambiente"}'::jsonb),
  ('LAC-002','8412345000027','Leche semidesnatada UHT Asturiana 1 L','lacteos.leche','UD',false,false, 4.00,0.80, 1.09, 48,120,180,'{"marca":"Asturiana","formato":"1 L","conservacion":"Ambiente"}'::jsonb),
  ('LAC-003','8412345000034','Leche desnatada UHT Central Lechera 1 L','lacteos.leche','UD',false,false, 4.00,0.79,1.07, 36, 96,180,'{"marca":"Central Lechera Asturiana","formato":"1 L"}'::jsonb),
  ('LAC-004','8412345000041','Nata líquida para cocinar 200 ml',    'lacteos.leche','UD',false,false, 4.00,0.85, 1.19, 12, 30,120,'{"marca":"President","formato":"200 ml"}'::jsonb),
  ('LAC-005','8412345000058','Yogur natural Danone pack 8x125 g',   'lacteos.yogures','UD',false,true, 4.00,1.45, 1.99, 16, 40, 28,'{"marca":"Danone","formato":"8x125 g"}'::jsonb),
  ('LAC-006','8412345000065','Yogur griego natural 500 g',          'lacteos.yogures','UD',false,true, 4.00,1.20, 1.69, 10, 24, 24,'{"marca":"Danone","formato":"500 g"}'::jsonb),
  ('LAC-007','8412345000072','Queso manchego curado 250 g',         'lacteos','UD',false,true, 4.00,3.40, 4.75,  8, 20,120,'{"marca":"García Baquero","denominacion":"D.O. Manchego"}'::jsonb),
  ('LAC-008','8412345000089','Queso fresco de Burgos 200 g',        'lacteos','UD',false,true, 4.00,1.35, 1.85,  8, 18, 21,'{"marca":"El Ventero","formato":"200 g"}'::jsonb),
  ('LAC-009','8412345000096','Mantequilla con sal 250 g',           'lacteos','UD',false,true, 4.00,1.90, 2.55,  8, 20, 90,'{"marca":"Arias","formato":"250 g"}'::jsonb),
  ('LAC-010','8412345000102','Flan de huevo pack 4x110 g',          'lacteos.yogures','UD',false,true, 4.00,1.10,1.55, 12, 30, 30,'{"marca":"Dhul","formato":"4x110 g"}'::jsonb),
  ('FRE-001','8412345000119','Plátano de Canarias',                 'frescos.frutas_verduras','KG',true,true,  4.00,1.05,1.59, 15, 40,  7,'{"origen":"Canarias","conservacion":"Ambiente"}'::jsonb),
  ('FRE-002','8412345000126','Manzana Golden',                      'frescos.frutas_verduras','KG',true,true,  4.00,0.95,1.45, 15, 35, 15,'{"origen":"Lleida","conservacion":"Cámara"}'::jsonb),
  ('FRE-003','8412345000133','Naranja de Valencia',                 'frescos.frutas_verduras','KG',true,true,  4.00,0.75,1.19, 20, 50, 10,'{"origen":"Valencia","conservacion":"Cámara"}'::jsonb),
  ('FRE-004','8412345000140','Tomate en rama',                      'frescos.frutas_verduras','KG',true,true,  4.00,1.35,2.10, 10, 30,  6,'{"origen":"Almería","conservacion":"Ambiente"}'::jsonb),
  ('FRE-005','8412345000157','Patata blanca',                       'frescos.frutas_verduras','KG',true,false, 4.00,0.62,0.95, 25, 60, 30,'{"origen":"Castilla y León","conservacion":"Almacén"}'::jsonb),
  ('FRE-006','8412345000164','Lechuga iceberg',                     'frescos.frutas_verduras','UD',false,true, 4.00,0.55,0.99, 10, 25,  5,'{"origen":"Murcia","conservacion":"Cámara"}'::jsonb),
  ('FRE-007','8412345000171','Cebolla dulce',                       'frescos.frutas_verduras','KG',true,false, 4.00,0.70,1.05, 15, 40, 20,'{"origen":"Valencia","conservacion":"Almacén"}'::jsonb),
  ('CAR-001','8412345000188','Pechuga de pollo fileteada',          'frescos.carniceria','KG',true,true, 10.00,4.20,6.25,  8, 20,  4,'{"origen":"Castellón","conservacion":"Cámara 0-4 ºC"}'::jsonb),
  ('CAR-002','8412345000195','Carne picada mixta bandeja 500 g',    'frescos.carniceria','UD',false,true,10.00,3.10,4.35,  6, 15,  3,'{"origen":"Valencia","conservacion":"Cámara 0-4 ºC"}'::jsonb),
  ('CAR-003','8412345000201','Chorizo ibérico 250 g',               'frescos.carniceria','UD',false,true,10.00,2.45,3.49,  6, 15, 60,'{"marca":"Casa Tarradellas","formato":"250 g"}'::jsonb),
  ('CAR-004','8412345000218','Lomo de cerdo en filetes',            'frescos.carniceria','KG',true,true, 10.00,5.10,7.25,  5, 12,  4,'{"origen":"Segovia","conservacion":"Cámara 0-4 ºC"}'::jsonb),
  ('DES-001','8412345000225','Aceite de oliva virgen extra 1 L',    'despensa','UD',false,false,10.00,5.20,6.95, 12, 30,540,'{"marca":"Carbonell","formato":"1 L"}'::jsonb),
  ('DES-002','8412345000232','Arroz redondo SOS 1 kg',              'despensa','UD',false,false,10.00,1.10,1.49, 10, 25,720,'{"marca":"SOS","formato":"1 kg"}'::jsonb),
  ('DES-003','8412345000249','Macarrones Gallo 500 g',              'despensa','UD',false,false,10.00,0.75,1.05, 12, 30,720,'{"marca":"Gallo","formato":"500 g"}'::jsonb),
  ('DES-004','8412345000256','Atún claro en aceite 3x80 g',         'despensa','UD',false,false,10.00,2.15,2.95, 10, 24,1095,'{"marca":"Calvo","formato":"3x80 g"}'::jsonb),
  ('DES-005','8412345000263','Tomate triturado Hida 400 g',         'despensa','UD',false,false,10.00,0.68,0.95, 12, 30,720,'{"marca":"Hida","formato":"400 g"}'::jsonb),
  ('DES-006','8412345000270','Harina de trigo 1 kg',                'despensa','UD',false,false,10.00,0.72,1.02,  8, 20,365,'{"marca":"Gallo","formato":"1 kg"}'::jsonb),
  ('BEB-001','8412345000287','Agua mineral Bezoya 1,5 L',           'bebidas','UD',false,false,10.00,0.28,0.49, 36, 96,540,'{"marca":"Bezoya","formato":"1,5 L"}'::jsonb),
  ('BEB-002','8412345000294','Refresco de cola 2 L',                'bebidas','UD',false,false,10.00,1.15,1.75, 18, 48,270,'{"marca":"Coca-Cola","formato":"2 L"}'::jsonb),
  ('BEB-003','8412345000300','Cerveza Estrella Damm 6x330 ml',      'bebidas','UD',false,false,21.00,3.45,4.65, 10, 24,240,'{"marca":"Estrella Damm","formato":"6x330 ml","alcohol":true}'::jsonb)
) AS v(sku, ean, name, cat_path, unit, weighted, perishable, tax, cost, price, min_stock, target_stock, shelf_life, attrs)
JOIN catalog.categories c
  ON c.path = v.cat_path::ltree
 AND c.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

-- Multi-proveedor: uno preferente por producto.
INSERT INTO catalog.product_suppliers (product_id, supplier_id, supplier_sku, pack_size, cost, is_preferred, lead_time_days)
SELECT p.id, s.id, v.supplier_sku, v.pack_size, v.cost, v.preferred, v.lead
FROM (VALUES
  ('LAC-001','LACT-01','LT-1001',12,0.78,true, 2),
  ('LAC-002','LACT-01','LT-1002',12,0.80,true, 2),
  ('LAC-005','LACT-01','LT-2005', 6,1.45,true, 2),
  ('LAC-007','LACT-01','LT-3007', 6,3.40,true, 2),
  ('FRE-001','FRUT-01','FP-PLA',  5,1.05,true, 1),
  ('FRE-002','FRUT-01','FP-MAN',  5,0.95,true, 1),
  ('FRE-005','FRUT-01','FP-PAT', 10,0.62,true, 1),
  ('CAR-001','CARN-01','CS-POL',  2,4.20,true, 2),
  ('CAR-002','CARN-01','CS-PIC',  4,3.10,true, 2),
  ('DES-001','DIST-01','DM-ACE1', 6,5.20,true, 3),
  ('DES-004','DIST-01','DM-ATU3',12,2.15,true, 3),
  ('BEB-001','DIST-01','DM-AGU6', 6,0.28,true, 3),
  ('BEB-003','DIST-01','DM-CER6', 4,3.45,true, 3)
) AS v(product_sku, supplier_code, supplier_sku, pack_size, cost, preferred, lead)
JOIN catalog.products p  ON p.sku = v.product_sku  AND p.store_id = pg_temp.seed_id('store')
JOIN catalog.suppliers s ON s.code = v.supplier_code AND s.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

-- =====================================================================
-- INVENTORY · ubicaciones, stock, lotes, movimientos y mermas
-- =====================================================================
INSERT INTO inventory.locations (store_id, code, name, type)
SELECT pg_temp.seed_id('store'), v.code, v.name, v.type::inventory.location_type
FROM (VALUES
  ('SALA',    'Sala de venta',      'SALA'),
  ('ALMACEN', 'Almacén',            'ALMACEN'),
  ('CAMARA',  'Cámara frigorífica', 'CAMARA'),
  ('CAJA',    'Zona de cajas',      'CAJA')
) AS v(code, name, type)
ON CONFLICT DO NOTHING;

INSERT INTO _seed_ids (key, id)
SELECT 'loc.sala', id FROM inventory.locations WHERE code = 'SALA'    AND store_id = pg_temp.seed_id('store')
ON CONFLICT (key) DO UPDATE SET id = EXCLUDED.id;
INSERT INTO _seed_ids (key, id)
SELECT 'loc.almacen', id FROM inventory.locations WHERE code = 'ALMACEN' AND store_id = pg_temp.seed_id('store')
ON CONFLICT (key) DO UPDATE SET id = EXCLUDED.id;
INSERT INTO _seed_ids (key, id)
SELECT 'loc.camara', id FROM inventory.locations WHERE code = 'CAMARA'  AND store_id = pg_temp.seed_id('store')
ON CONFLICT (key) DO UPDATE SET id = EXCLUDED.id;
INSERT INTO _seed_ids (key, id)
SELECT 'loc.caja', id FROM inventory.locations WHERE code = 'CAJA'    AND store_id = pg_temp.seed_id('store')
ON CONFLICT (key) DO UPDATE SET id = EXCLUDED.id;

-- Stock inicial. Hay 5 productos POR DEBAJO de su mínimo a propósito, para que las
-- reglas del motor se disparen en la demo: LAC-001 (12/48), LAC-008 (7/8),
-- FRE-001 (8/15), CAR-002 (3/6) y BEB-001 (20/36), todos ellos en SALA.
INSERT INTO inventory.stock (store_id, product_id, location_id, qty, reserved_qty)
SELECT pg_temp.seed_id('store'), p.id, pg_temp.seed_id(v.loc_key), v.qty, 0
FROM (VALUES
  ('LAC-001','loc.sala',   12.000),  -- mínimo 48  => ROTURA
  ('LAC-002','loc.sala',   60.000),
  ('LAC-003','loc.sala',   42.000),
  ('LAC-005','loc.sala',   18.000),
  ('LAC-007','loc.sala',    9.000),
  ('LAC-008','loc.sala',    7.000),
  ('FRE-001','loc.sala',    8.000),  -- mínimo 15  => ROTURA
  ('FRE-002','loc.sala',   22.000),
  ('FRE-003','loc.sala',   26.000),
  ('FRE-004','loc.sala',   14.000),
  ('FRE-006','loc.sala',   12.000),
  ('CAR-001','loc.sala',    9.000),
  ('CAR-002','loc.sala',    3.000),  -- mínimo 6   => ROTURA
  ('CAR-003','loc.sala',    8.000),
  ('DES-001','loc.sala',   16.000),
  ('DES-002','loc.sala',   14.000),
  ('DES-004','loc.sala',   12.000),
  ('BEB-001','loc.sala',   20.000),  -- mínimo 36  => ROTURA
  ('BEB-002','loc.sala',   26.000),
  ('BEB-003','loc.sala',   12.000),
  ('LAC-001','loc.almacen',36.000),
  ('LAC-002','loc.almacen',72.000),
  ('LAC-003','loc.almacen',60.000),
  ('LAC-005','loc.almacen',24.000),
  ('LAC-007','loc.almacen',12.000),
  ('FRE-002','loc.almacen',30.000),
  ('FRE-003','loc.almacen',40.000),
  ('FRE-005','loc.almacen',80.000),
  ('FRE-007','loc.almacen',45.000),
  ('CAR-001','loc.almacen',14.000),
  ('CAR-004','loc.almacen', 8.000),
  ('DES-001','loc.almacen',24.000),
  ('DES-003','loc.almacen',36.000),
  ('DES-005','loc.almacen',24.000),
  ('DES-006','loc.almacen',20.000),
  ('BEB-001','loc.almacen',60.000),
  ('BEB-002','loc.almacen',40.000)
) AS v(sku, loc_key, qty)
JOIN catalog.products p ON p.sku = v.sku AND p.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

-- Carga inicial de movimientos, derivada del propio stock para que cuadre.
INSERT INTO inventory.stock_movements (store_id, product_id, location_id, type, qty, unit_cost, reason_code, ref_type, note)
SELECT s.store_id, s.product_id, s.location_id, 'ENTRADA', s.qty, p.cost, 'CARGA_INICIAL', 'seed',
       'Carga inicial de demostración'
FROM inventory.stock s
JOIN catalog.products p ON p.id = s.product_id
WHERE s.store_id = pg_temp.seed_id('store')
  AND NOT EXISTS (
    SELECT 1 FROM inventory.stock_movements m
    WHERE m.store_id = s.store_id AND m.ref_type = 'seed'
  );

-- 7 lotes; dos de ellos caducan en menos de 3 días (disparan la regla de caducidades).
INSERT INTO inventory.lots (store_id, product_id, location_id, batch_code, expiry_date, qty, unit_cost)
SELECT pg_temp.seed_id('store'), p.id, pg_temp.seed_id(v.loc_key), v.batch, v.expiry, v.qty, p.cost
FROM (VALUES
  ('LAC-005','loc.camara','YOG-2601', CURRENT_DATE + 2,  8.000),  -- caduca en 2 días
  ('FRE-006','loc.camara','LEC-2601', CURRENT_DATE + 1,  6.000),  -- caduca en 1 día
  ('FRE-001','loc.sala',  'PLA-2601', CURRENT_DATE + 5,  8.000),
  ('FRE-004','loc.sala',  'TOM-2601', CURRENT_DATE + 4,  9.000),
  ('CAR-001','loc.camara','POL-2601', CURRENT_DATE + 3,  5.000),
  ('CAR-002','loc.camara','PIC-2601', CURRENT_DATE + 6,  3.000),
  ('LAC-008','loc.camara','QUE-2601', CURRENT_DATE + 12, 6.000)
) AS v(sku, loc_key, batch, expiry, qty)
JOIN catalog.products p ON p.sku = v.sku AND p.store_id = pg_temp.seed_id('store')
WHERE NOT EXISTS (
  SELECT 1 FROM inventory.lots x WHERE x.store_id = pg_temp.seed_id('store')
);

INSERT INTO inventory.wastage (store_id, product_id, lot_id, location_id, qty, reason_code, cost_impact, user_id, notes)
SELECT pg_temp.seed_id('store'), p.id, l.id, pg_temp.seed_id(v.loc_key),
       v.qty, v.reason::inventory.wastage_reason, ROUND(v.qty * p.cost, 2), u.id, v.notes
FROM (VALUES
  ('LAC-005','YOG-2601','loc.camara',1.000,'CADUCADO','Yogur retirado del lineal por caducidad'),
  ('FRE-006','LEC-2601','loc.camara',2.000,'ROTO',    'Lechuga dañada al colocar en el lineal'),
  ('FRE-001','PLA-2601','loc.sala',  1.500,'CADUCADO','Plátano sobremaduro retirado de exposición')
) AS v(sku, batch, loc_key, qty, reason, notes)
JOIN catalog.products p ON p.sku = v.sku AND p.store_id = pg_temp.seed_id('store')
LEFT JOIN inventory.lots l ON l.product_id = p.id AND l.batch_code = v.batch
LEFT JOIN core.users u ON u.email = 'sala1@malato.es'::citext
WHERE NOT EXISTS (
  SELECT 1 FROM inventory.wastage w WHERE w.store_id = pg_temp.seed_id('store')
);

-- =====================================================================
-- TASKS · plantillas, tareas y reglas del motor
-- =====================================================================
INSERT INTO tasks.task_templates (store_id, code, name, description, default_priority, estimated_minutes,
                                  required_role, checklist, sla_minutes, requires_evidence)
SELECT pg_temp.seed_id('store'), v.code, v.name, v.description, v.priority::tasks.task_priority,
       v.minutes, v.role, v.checklist, v.sla, v.evidence
FROM (VALUES
  ('REPOSICION_PRIORITARIA','Reposición prioritaria','Reponer en sala un producto sin stock, desde almacén.',
   'ALTA', 20,'OPERADORA','["Localizar el producto en almacén","Reponer en el lineal asignado","Comprobar el precio en el TPV"]'::jsonb, 30,false),
  ('REVISION_CADUCIDADES','Revisión de caducidades','Retirar y registrar producto próximo a caducar.',
   'ALTA', 25,'OPERADORA','["Recorrer el lineal indicado","Separar lo que caduca en menos de 3 días","Registrar la merma"]'::jsonb, 45,true),
  ('LIMPIEZA_LINEAL','Limpieza de lineal','Limpieza y orden del lineal asignado.',
   'BAJA', 15,'OPERADORA','["Retirar el producto de la balda","Limpiar la balda","Recolocar por fecha de caducidad"]'::jsonb, 60,false),
  ('CONTROL_CAJA','Control de caja','Arqueo parcial y revisión de la sesión de caja.',
   'MEDIA',10,'COORDINADORA','["Comprobar el fondo de caja","Contar el efectivo","Registrar el arqueo parcial"]'::jsonb, 20,false),
  ('ATENCION_PEDIDO','Atención a pedido de proveedor','Recepcionar y colocar el pedido del proveedor.',
   'ALTA', 45,'OPERADORA','["Comprobar el albarán","Verificar cantidades y fechas","Registrar incidencias","Colocar en almacén"]'::jsonb, 60,false),
  ('REPOSICION_BEBIDAS','Refuerzo de reposición de bebidas','Reposición completa del lineal de bebidas.',
   'MEDIA',20,'OPERADORA','["Revisar huecos en el lineal","Bajar género de almacén","Reponer y orientar etiquetas"]'::jsonb, 40,false),
  ('RECUENTO_LINEAL','Recuento de lineal','Contar el género del lineal y ajustar el stock real en el sistema.',
   'MEDIA',30,'OPERADORA','["Recorrer el lineal indicado","Contar unidades producto a producto","Registrar el recuento y la diferencia"]'::jsonb, 90,false)
) AS v(code, name, description, priority, minutes, role, checklist, sla, evidence)
ON CONFLICT DO NOTHING;

-- 5 reglas ECA reales: event_type + condition {all:[...]} + actions [{type,params}]
-- OJO al leer "role": "OPERADORA" en las acciones: es el rol MÍNIMO, no el exclusivo.
-- El reparto (LEAST_LOADED) busca entre TODAS las personas de sala con nivel >= 10,
-- es decir las 2 operadoras y las 3 coordinadoras: 5 candidatas. Si los roles fueran
-- excluyentes, dos personas cargarían con todo el trabajo de reposición mientras las
-- otras tres miran. Gerencia queda fuera del reparto porque no opera en tienda.
INSERT INTO rules.rules (store_id, code, name, description, event_type, condition, actions,
                         priority, is_active, cooldown_minutes, max_per_day, valid_from, created_by)
SELECT pg_temp.seed_id('store'), v.code, v.name, v.description, v.event_type, v.condition, v.actions,
       v.priority, v.is_active, v.cooldown, v.max_day, now(), u.id
FROM (VALUES
  (
    'LUNES_LACTEOS_STOCK_BAJO',
    'Lunes con poca afluencia y lácteos bajo mínimo',
    'Reposición prioritaria de lácteos al empezar la semana.',
    'stock.below_minimum',
    $cond${
      "all": [
        { "fact": "calendar.weekday", "op": "eq", "value": "MONDAY" },
        { "fact": "store.affluence", "op": "eq", "value": "LOW" },
        { "fact": "inventory.stock_ratio", "op": "lt", "value": 0.30,
          "params": { "categoryPath": "lacteos" } }
      ]
    }$cond$::jsonb,
    $act$[
      { "type": "CREATE_TASK", "params": {
          "template_code": "REPOSICION_PRIORITARIA",
          "assignee_strategy": "LEAST_LOADED",
          "role": "OPERADORA",
          "priority": "ALTA",
          "due_in_minutes": 30,
          "payload": { "categoryPath": "lacteos", "origin": "RULE" } } },
      { "type": "NOTIFY", "params": {
          "target": "ROLE", "role": "COORDINADORA", "severity": "AVISO",
          "title": "Reposición prioritaria de lácteos generada" } }
    ]$act$::jsonb,
    10, true, 120, 3
  ),
  (
    'VIERNES_TARDE_REFUERZO_BEBIDAS',
    'Viernes tarde con afluencia alta',
    'Refuerzo de reposición de bebidas antes del pico de tarde.',
    'schedule.weekday_window',
    $cond${
      "all": [
        { "fact": "calendar.weekday", "op": "eq", "value": "FRIDAY" },
        { "fact": "calendar.time_window", "op": "in", "value": ["17:00", "21:00"] },
        { "fact": "store.affluence_forecast", "op": "eq", "value": "HIGH" }
      ]
    }$cond$::jsonb,
    $act$[
      { "type": "CREATE_TASK", "params": {
          "template_code": "REPOSICION_BEBIDAS",
          "assignee_strategy": "LEAST_LOADED",
          "role": "OPERADORA",
          "priority": "MEDIA",
          "due_in_minutes": 45,
          "slots": 2,
          "payload": { "categoryPath": "bebidas", "origin": "RULE" } } }
    ]$act$::jsonb,
    20, true, 240, 1
  ),
  (
    'LOTE_PROXIMO_CADUCIDAD',
    'Lote a menos de 3 días de caducar',
    'Tarea de revisión y notificación a coordinación.',
    'lot.expiring_soon',
    $cond${
      "all": [
        { "fact": "inventory.days_to_expiry", "op": "lte", "value": 3 },
        { "fact": "inventory.lot_qty", "op": "gt", "value": 0 }
      ]
    }$cond$::jsonb,
    $act$[
      { "type": "CREATE_TASK", "params": {
          "template_code": "REVISION_CADUCIDADES",
          "assignee_strategy": "ROUND_ROBIN",
          "role": "OPERADORA",
          "priority": "ALTA",
          "due_in_minutes": 60,
          "payload": { "lotId": "$event.lotId", "productId": "$event.productId", "origin": "RULE" } } },
      { "type": "NOTIFY", "params": {
          "target": "ROLE", "role": "COORDINADORA", "severity": "AVISO",
          "title": "Lote próximo a caducar" } }
    ]$act$::jsonb,
    30, true, 0, 10
  ),
  (
    'DESCUADRE_CAJA',
    'Descuadre de caja superior a 5 euros',
    'Avisa a gerencia con severidad alta.',
    'cash_session.discrepancy',
    $cond${
      "all": [
        { "fact": "pos.cash_difference_abs", "op": "gt", "value": 5 }
      ]
    }$cond$::jsonb,
    $act$[
      { "type": "NOTIFY", "params": {
          "target": "ROLE", "role": "GERENCIA", "severity": "GRAVE",
          "title": "Descuadre de caja superior a 5 euros",
          "channels": ["IN_APP", "EMAIL"] } }
    ]$act$::jsonb,
    5, true, 30, 5
  ),
  (
    'TAREA_VENCIDA_REASIGNAR',
    'Tarea vencida más de 30 minutos',
    'Reasigna la tarea a quien menos carga tenga y avisa a coordinación.',
    'task.overdue',
    $cond${
      "all": [
        { "fact": "tasks.minutes_overdue", "op": "gt", "value": 30 },
        { "fact": "tasks.status", "op": "in", "value": ["ASIGNADA", "EN_CURSO"] }
      ]
    }$cond$::jsonb,
    $act$[
      { "type": "REASSIGN_TASK", "params": {
          "strategy": "LEAST_LOADED",
          "role": "OPERADORA",
          "exclude_current_assignee": true,
          "reason": "Tarea vencida más de 30 minutos" } },
      { "type": "NOTIFY", "params": {
          "target": "ROLE", "role": "COORDINADORA", "severity": "AVISO",
          "title": "Tarea reasignada por vencimiento" } }
    ]$act$::jsonb,
    40, true, 15, 20
  )
) AS v(code, name, description, event_type, condition, actions, priority, is_active, cooldown, max_day)
LEFT JOIN core.users u ON u.email = 'gerencia@malato.es'::citext
ON CONFLICT DO NOTHING;

-- Sobrescritura táctica de una coordinadora para el día de hoy.
INSERT INTO rules.rule_overrides (store_id, rule_id, override_date, target_user_id, action_type, reason, by_user_id, expires_at)
SELECT pg_temp.seed_id('store'), r.id, CURRENT_DATE, u.id, 'REASSIGN_TASK',
       'Refuerzo de sala por ausencia de una operadora: coordina el turno', c.id, now() + interval '1 day'
FROM rules.rules r
JOIN core.users u ON u.email = 'coordinacion3@malato.es'::citext
JOIN core.users c ON c.email = 'coordinacion1@malato.es'::citext
WHERE r.code = 'TAREA_VENCIDA_REASIGNAR'
  AND r.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

-- Tareas del día (una de ellas ya vencida, para la demo del motor).
INSERT INTO tasks.tasks (store_id, template_id, title, description, priority, status, assignee_id,
                         location_id, due_at, created_by_rule_id, payload)
SELECT pg_temp.seed_id('store'), t.id, v.title, v.description, v.priority::tasks.task_priority,
       v.status::tasks.task_status, u.id, pg_temp.seed_id(v.loc_key),
       now() + make_interval(mins => v.due_offset), rl.id, v.payload::jsonb
FROM (VALUES
  ('REPOSICION_PRIORITARIA','Reponer leche entera 1 L en sala','Stock por debajo del mínimo en el lineal de leche.',
   'ALTA','ASIGNADA','sala1@malato.es','loc.sala',  30,'LUNES_LACTEOS_STOCK_BAJO','{"productSku":"LAC-001","qty":36,"origin":"RULE"}'),
  ('REVISION_CADUCIDADES','Retirar yogur natural próximo a caducar','El lote YOG-2601 caduca en 2 días.',
   'ALTA','EN_CURSO','sala2@malato.es','loc.camara', 45,'LOTE_PROXIMO_CADUCIDAD','{"lotBatch":"YOG-2601","productSku":"LAC-005","origin":"RULE"}'),
  ('REPOSICION_BEBIDAS','Reforzar el lineal de bebidas','Huecos detectados en aguas y refrescos.',
   'MEDIA','PENDIENTE',NULL,'loc.sala', 90,'VIERNES_TARDE_REFUERZO_BEBIDAS','{"categoryPath":"bebidas","origin":"RULE"}'),
  ('LIMPIEZA_LINEAL','Limpieza del lineal de conservas','Tarea de cierre del turno de mañana.',
   'BAJA','ASIGNADA','coordinacion3@malato.es','loc.sala', -45,NULL,'{"shelf":"conservas","origin":"MANUAL"}')
) AS v(template_code, title, description, priority, status, email, loc_key, due_offset, rule_code, payload)
JOIN tasks.task_templates t ON t.code = v.template_code AND t.store_id = pg_temp.seed_id('store')
LEFT JOIN core.users u ON u.email = v.email::citext
LEFT JOIN rules.rules rl ON rl.code = v.rule_code AND rl.store_id = pg_temp.seed_id('store')
WHERE NOT EXISTS (
  SELECT 1 FROM tasks.tasks x WHERE x.store_id = pg_temp.seed_id('store')
);

INSERT INTO tasks.task_events (task_id, store_id, type, to_user_id, to_status, comment)
SELECT t.id, t.store_id, 'CREADA', t.assignee_id, t.status,
       'Tarea generada por el motor de reglas (demostración)'
FROM tasks.tasks t
WHERE t.store_id = pg_temp.seed_id('store')
  AND NOT EXISTS (SELECT 1 FROM tasks.task_events e WHERE e.task_id = t.id);

-- =====================================================================
-- POS · cajas, dos sesiones históricas cerradas y tres ventas
-- =====================================================================
INSERT INTO pos.registers (store_id, code, name, location_id)
SELECT pg_temp.seed_id('store'), v.code, v.name, pg_temp.seed_id('loc.caja')
FROM (VALUES ('CAJA-01','Caja 1'), ('CAJA-02','Caja 2')) AS v(code, name)
ON CONFLICT DO NOTHING;

INSERT INTO pos.cash_sessions (store_id, register_id, status, opened_by, opened_at, closed_by, closed_at,
                               opening_float, expected_cash, counted_cash, difference, notes)
SELECT pg_temp.seed_id('store'), r.id, 'CERRADA', uo.id,
       (CURRENT_DATE - 1 + time '08:00') AT TIME ZONE 'Europe/Madrid',
       uc.id,
       (CURRENT_DATE - 1 + time '21:00') AT TIME ZONE 'Europe/Madrid',
       v.float, v.expected, v.counted, v.counted - v.expected, v.notes
FROM (VALUES
  ('CAJA-01','sala1@malato.es','sala2@malato.es',150.00,1284.50,1284.50,'Cierre sin incidencias'),
  ('CAJA-02','sala2@malato.es','sala1@malato.es',150.00, 962.30, 957.10,'Faltan 5,20 euros, pendiente de revisión')
) AS v(register_code, open_email, close_email, float, expected, counted, notes)
JOIN pos.registers r  ON r.code = v.register_code AND r.store_id = pg_temp.seed_id('store')
JOIN core.users   uo ON uo.email = v.open_email::citext
JOIN core.users   uc ON uc.email = v.close_email::citext
-- Sin UNIQUE sobre (register_id, opened_at): la idempotencia se garantiza aquí.
WHERE NOT EXISTS (
  SELECT 1 FROM pos.cash_sessions x WHERE x.store_id = pg_temp.seed_id('store')
);

INSERT INTO pos.sales (store_id, cash_session_id, register_id, ticket_number, status, subtotal,
                       discount_total, tax_total, total, operator_id, sold_at, synced_at)
SELECT pg_temp.seed_id('store'), cs.id, cs.register_id, v.ticket, 'COMPLETADA'::pos.sale_status,
       v.subtotal, v.discount, v.tax, v.total, u.id, cs.closed_at - interval '1 hour', cs.closed_at
FROM (VALUES
  ('CAJA-01','T-2601-000101', 9.75,0.00,0.85,10.60,'sala1@malato.es'),
  ('CAJA-01','T-2601-000102',16.83,1.00,1.52,17.35,'sala1@malato.es'),
  ('CAJA-02','T-2601-000103',10.32,0.00,2.06,12.38,'sala2@malato.es')
) AS v(register_code, ticket, subtotal, discount, tax, total, email)
JOIN pos.registers     r  ON r.code = v.register_code AND r.store_id = pg_temp.seed_id('store')
JOIN pos.cash_sessions cs ON cs.register_id = r.id AND cs.status = 'CERRADA'
JOIN core.users        u  ON u.email = v.email::citext
ON CONFLICT DO NOTHING;

-- El ticket es único por caja, así que la búsqueda se hace por (caja, ticket).
INSERT INTO pos.sale_lines (sale_id, line_no, product_id, description, qty, unit_price, discount, tax_rate, line_total)
SELECT s.id, v.line_no, p.id, p.name, v.qty, v.unit_price, v.discount, p.tax_rate, v.line_total
FROM (VALUES
  ('CAJA-01','T-2601-000101',1,'LAC-001', 2.000,1.0500,0.00, 2.10),
  ('CAJA-01','T-2601-000101',2,'DES-004', 2.000,2.9500,0.00, 5.90),
  ('CAJA-01','T-2601-000101',3,'BEB-002', 1.000,1.7500,0.00, 1.75),
  ('CAJA-01','T-2601-000102',1,'CAR-001', 1.200,6.2500,1.00, 6.50),
  ('CAJA-01','T-2601-000102',2,'FRE-003', 2.000,1.1900,0.00, 2.38),
  ('CAJA-01','T-2601-000102',3,'DES-001', 1.000,6.9500,0.00, 6.95),
  ('CAJA-02','T-2601-000103',1,'BEB-003', 2.000,4.6500,0.00, 9.30),
  ('CAJA-02','T-2601-000103',2,'DES-006', 1.000,1.0200,0.00, 1.02)
) AS v(register_code, ticket, line_no, sku, qty, unit_price, discount, line_total)
JOIN pos.registers    r ON r.code = v.register_code AND r.store_id = pg_temp.seed_id('store')
JOIN pos.sales        s ON s.register_id = r.id AND s.ticket_number = v.ticket
JOIN catalog.products p ON p.sku = v.sku AND p.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

INSERT INTO pos.payments (sale_id, method, amount, change_given)
SELECT s.id, v.method::pos.payment_method, v.amount, v.change
FROM (VALUES
  ('CAJA-01','T-2601-000101','EFECTIVO',20.00, 9.40),
  ('CAJA-01','T-2601-000102','TARJETA', 17.35, 0.00),
  ('CAJA-02','T-2601-000103','EFECTIVO',20.00, 7.62)
) AS v(register_code, ticket, method, amount, change)
JOIN pos.registers r ON r.code = v.register_code AND r.store_id = pg_temp.seed_id('store')
JOIN pos.sales     s ON s.register_id = r.id AND s.ticket_number = v.ticket
-- Sin UNIQUE sobre (sale_id, method): la idempotencia se garantiza aquí.
WHERE NOT EXISTS (SELECT 1 FROM pos.payments x WHERE x.sale_id = s.id);

-- =====================================================================
-- NOTIFY · suscripciones y avisos de ejemplo
-- =====================================================================
INSERT INTO notify.notification_subscriptions (store_id, user_id, type, channels)
SELECT pg_temp.seed_id('store'), u.id, v.type, v.channels
FROM core.users u
JOIN core.roles r ON r.id = u.role_id
JOIN (VALUES
  ('GERENCIA',     '*',                   '["IN_APP","EMAIL"]'::jsonb),
  ('COORDINADORA', 'stock.below_minimum', '["IN_APP","PUSH"]'::jsonb),
  ('COORDINADORA', 'task.overdue',        '["IN_APP","PUSH"]'::jsonb),
  ('OPERADORA',    'task.assigned',       '["IN_APP"]'::jsonb)
) AS v(role_code, type, channels) ON v.role_code = r.code
WHERE u.store_id = pg_temp.seed_id('store')
ON CONFLICT DO NOTHING;

-- Avisos de ejemplo, dirigidos al ROL COORDINADORA (target_user_id NULL), no a una
-- persona concreta: los ven las tres y cada una los marca leídos por su cuenta en
-- notify.notification_reads. Antes apuntaban a una operadora teniendo
-- target_role = 'COORDINADORA', lo cual era incoherente: quien debía atenderlos
-- no era quien los estaba recibiendo.
INSERT INTO notify.notifications (store_id, type, severity, title, body, payload,
                                  target_role, target_user_id, ref_type, ref_id, dedup_key)
SELECT pg_temp.seed_id('store'), v.type, v.severity::notify.severity, v.title, v.body,
       jsonb_build_object('sku', v.sku), v.target_role, u.id, 'catalog.products', p.id, v.dedup_key
FROM (VALUES
  ('stock.below_minimum','GRAVE','Rotura de stock: leche entera 1 L',
   'Quedan 12 unidades en sala y el mínimo es 48.','LAC-001','COORDINADORA',NULL,'seed:stock:LAC-001'),
  ('stock.below_minimum','GRAVE','Rotura de stock: plátano de Canarias',
   'Quedan 8 kg en sala y el mínimo es 15.','FRE-001','COORDINADORA',NULL,'seed:stock:FRE-001'),
  ('lot.expiring_soon','AVISO','Lote próximo a caducar: yogur natural',
   'El lote YOG-2601 caduca en 2 días.','LAC-005','COORDINADORA',NULL,'seed:lot:YOG-2601')
) AS v(type, severity, title, body, sku, target_role, target_email, dedup_key)
JOIN catalog.products p ON p.sku = v.sku AND p.store_id = pg_temp.seed_id('store')
LEFT JOIN core.users   u ON u.email = v.target_email::citext
ON CONFLICT DO NOTHING;

-- =====================================================================
-- ANALYTICS · serie de KPIs de los últimos días
-- =====================================================================
INSERT INTO analytics.kpi_snapshots (store_id, kpi_code, date, period, value, dimensions)
SELECT pg_temp.seed_id('store'), v.kpi_code, CURRENT_DATE - v.days_ago, 'DAY', v.value, v.dimensions
FROM (VALUES
  ('sales.total',     1, 2380.45, '{"canal":"TIENDA"}'::jsonb),
  ('sales.total',     2, 2214.80, '{"canal":"TIENDA"}'::jsonb),
  ('sales.total',     3, 1976.30, '{"canal":"TIENDA"}'::jsonb),
  ('sales.total',     4, 2455.10, '{"canal":"TIENDA"}'::jsonb),
  ('sales.total',     5, 2610.75, '{"canal":"TIENDA"}'::jsonb),
  ('margin.percent',  1,   27.40, '{}'::jsonb),
  ('margin.percent',  2,   26.90, '{}'::jsonb),
  ('margin.percent',  3,   28.10, '{}'::jsonb),
  ('margin.percent',  4,   27.05, '{}'::jsonb),
  ('margin.percent',  5,   26.60, '{}'::jsonb),
  ('wastage.cost',    1,   38.20, '{}'::jsonb),
  ('wastage.cost',    2,   29.75, '{}'::jsonb),
  ('wastage.cost',    3,   44.10, '{}'::jsonb),
  ('wastage.cost',    4,   31.60, '{}'::jsonb),
  ('wastage.cost',    5,   26.95, '{}'::jsonb)
) AS v(kpi_code, days_ago, value, dimensions)
ON CONFLICT DO NOTHING;

COMMIT;
