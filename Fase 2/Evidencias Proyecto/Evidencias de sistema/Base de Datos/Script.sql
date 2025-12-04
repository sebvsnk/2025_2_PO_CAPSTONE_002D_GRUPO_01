-- Esquema APT
CREATE SCHEMA IF NOT EXISTS apt;

-- =========================================================
-- Tabla: usuario
-- =========================================================
CREATE TABLE apt.usuario (
  id               BIGSERIAL PRIMARY KEY,
  nombre           TEXT NOT NULL,
  email            TEXT UNIQUE,
  rol              TEXT NOT NULL DEFAULT 'MECANICO'
                     CHECK (rol IN (
                       'MECANICO',
                       'SUPERVISOR',
                       'PORTERIA',
                       'ADMIN',
                       'ANALISTA',
                       'CHOFER',
                       'GUARDIA'
                     )),
  external_id      UUID REFERENCES auth.users(id),
  creado_en        TIMESTAMPTZ NOT NULL DEFAULT now(),
  rut              TEXT,
  numero_telefonico TEXT
);

-- =========================================================
-- Tabla: vehiculo
-- =========================================================
CREATE TABLE apt.vehiculo (
  id         BIGSERIAL PRIMARY KEY,
  patente    VARCHAR NOT NULL
               CHECK (
                 patente ~* '^[A-Z]{2}-?[0-9]{4}$'
                 OR patente ~* '^[A-Z]{4}-?[0-9]{2}$'
               ),
  marca      TEXT,
  modelo     TEXT,
  creado_en  TIMESTAMPTZ NOT NULL DEFAULT now(),
  chofer_id  BIGINT REFERENCES apt.usuario(id)
);

-- =========================================================
-- Tabla: estado
-- (catálogo genérico de estados: OT, tarea, etc.)
-- =========================================================
CREATE TABLE apt.estado (
  id          BIGSERIAL PRIMARY KEY,
  tipo        TEXT NOT NULL,
  code        TEXT NOT NULL,
  label       TEXT NOT NULL,
  descripcion TEXT,
  orden       INTEGER NOT NULL DEFAULT 100,
  activo      BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: ot (Orden de Trabajo)
-- =========================================================
CREATE TABLE apt.ot (
  id             BIGSERIAL PRIMARY KEY,
  vehiculo_id    BIGINT NOT NULL REFERENCES apt.vehiculo(id),
  estado_id      BIGINT REFERENCES apt.estado(id),
  descripcion    TEXT,
  fecha_apertura TIMESTAMPTZ NOT NULL DEFAULT now(),
  fecha_cierre   TIMESTAMPTZ,
  creado_por     BIGINT,              -- opcionalmente FK a usuario
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: tarea
-- =========================================================
CREATE TABLE apt.tarea (
  id             BIGSERIAL PRIMARY KEY,
  ot_id          BIGINT NOT NULL REFERENCES apt.ot(id),
  nombre         TEXT NOT NULL,
  estado_id      BIGINT REFERENCES apt.estado(id),
  inicio         TIMESTAMPTZ,
  fin            TIMESTAMPTZ,
  responsable    BIGINT,              -- opcionalmente FK a usuario
  creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: pausa
-- =========================================================
CREATE TABLE apt.pausa (
  id        BIGSERIAL PRIMARY KEY,
  tarea_id  BIGINT NOT NULL REFERENCES apt.tarea(id),
  motivo    TEXT NOT NULL,
  inicio    TIMESTAMPTZ NOT NULL DEFAULT now(),
  fin       TIMESTAMPTZ
);

-- =========================================================
-- Tabla: repuesto
-- =========================================================
CREATE TABLE apt.repuesto (
  id            BIGSERIAL PRIMARY KEY,
  codigo        TEXT UNIQUE,
  descripcion   TEXT NOT NULL,
  unidad_medida TEXT NOT NULL DEFAULT 'unidad',
  activo        BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: tarea_repuesto (repuestos usados por tarea)
-- =========================================================
CREATE TABLE apt.tarea_repuesto (
  id          BIGSERIAL PRIMARY KEY,
  tarea_id    BIGINT NOT NULL REFERENCES apt.tarea(id),
  repuesto_id BIGINT NOT NULL REFERENCES apt.repuesto(id),
  cantidad    NUMERIC NOT NULL CHECK (cantidad > 0),
  observacion TEXT,
  creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: evidencia (archivos asociados a tareas)
-- =========================================================
CREATE TABLE apt.evidencia (
  id           BIGSERIAL PRIMARY KEY,
  tarea_id     BIGINT NOT NULL REFERENCES apt.tarea(id),
  path         TEXT NOT NULL,
  mime_type    VARCHAR,
  tamano_bytes BIGINT,
  subido_por   BIGINT REFERENCES apt.usuario(id),
  fecha_subida TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: tarea_repuesto_evidencia
-- (relación N a N entre repuestos usados y evidencias)
-- =========================================================
CREATE TABLE apt.tarea_repuesto_evidencia (
  tarea_repuesto_id BIGINT NOT NULL REFERENCES apt.tarea_repuesto(id),
  evidencia_id      BIGINT NOT NULL REFERENCES apt.evidencia(id),
  PRIMARY KEY (tarea_repuesto_id, evidencia_id)
);

-- =========================================================
-- Tabla: bitacora_porteria
-- =========================================================
CREATE TABLE apt.bitacora_porteria (
  id          BIGSERIAL PRIMARY KEY,
  vehiculo_id BIGINT NOT NULL REFERENCES apt.vehiculo(id),
  tipo        TEXT NOT NULL
                CHECK (tipo IN ('ENTRADA', 'SALIDA')),
  fecha_hora  TIMESTAMPTZ NOT NULL DEFAULT now(),
  usuario_id  BIGINT REFERENCES apt.usuario(id)
);

-- =========================================================
-- Tabla: vehiculo_patente_hist
-- (histórico de patentes por vehículo)
-- =========================================================
CREATE TABLE apt.vehiculo_patente_hist (
  id          BIGSERIAL PRIMARY KEY,
  vehiculo_id BIGINT NOT NULL REFERENCES apt.vehiculo(id),
  patente     TEXT NOT NULL,
  desde       TIMESTAMPTZ NOT NULL DEFAULT now(),
  hasta       TIMESTAMPTZ
);

-- =========================================================
-- Tabla: audit_log
-- =========================================================
CREATE TABLE apt.audit_log (
  id          BIGSERIAL PRIMARY KEY,
  usuario_id  BIGINT REFERENCES apt.usuario(id),
  action_type TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id   BIGINT,
  details     JSONB,
  creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- Tabla: _delete_queue (cola para borrado diferido de evidencias)
-- =========================================================
CREATE TABLE apt._delete_queue (
  id          BIGSERIAL PRIMARY KEY,
  kind        TEXT NOT NULL CHECK (kind = 'evidencia'),
  ref_id      BIGINT,
  path        TEXT NOT NULL,
  queued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  processed_at TIMESTAMPTZ
);
