-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE apt._delete_queue (
  id bigint NOT NULL DEFAULT nextval('apt._delete_queue_id_seq'::regclass),
  kind text NOT NULL CHECK (kind = 'evidencia'::text),
  ref_id bigint,
  path text NOT NULL,
  queued_at timestamp with time zone NOT NULL DEFAULT now(),
  processed_at timestamp with time zone,
  CONSTRAINT _delete_queue_pkey PRIMARY KEY (id)
);
CREATE TABLE apt.bitacora_porteria (
  id bigint NOT NULL DEFAULT nextval('apt.bitacora_porteria_id_seq'::regclass),
  vehiculo_id bigint NOT NULL,
  tipo text NOT NULL CHECK (tipo = ANY (ARRAY['ENTRADA'::text, 'SALIDA'::text])),
  fecha_hora timestamp with time zone NOT NULL DEFAULT now(),
  usuario_id bigint,
  CONSTRAINT bitacora_porteria_pkey PRIMARY KEY (id),
  CONSTRAINT bitacora_porteria_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES apt.vehiculo(id),
  CONSTRAINT bitacora_porteria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES apt.usuario(id)
);
CREATE TABLE apt.estado (
  id bigint NOT NULL DEFAULT nextval('apt.estado_id_seq'::regclass),
  tipo text NOT NULL,
  code text NOT NULL,
  label text NOT NULL,
  descripcion text,
  orden integer NOT NULL DEFAULT 100,
  activo boolean NOT NULL DEFAULT true,
  creado_en timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT estado_pkey PRIMARY KEY (id)
);
CREATE TABLE apt.evidencia (
  id bigint NOT NULL DEFAULT nextval('apt.evidencia_id_seq'::regclass),
  tarea_id bigint NOT NULL,
  path text NOT NULL,
  mime_type character varying,
  tamano_bytes bigint,
  subido_por bigint,
  fecha_subida timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT evidencia_pkey PRIMARY KEY (id),
  CONSTRAINT evidencia_tarea_id_fkey FOREIGN KEY (tarea_id) REFERENCES apt.tarea(id),
  CONSTRAINT evidencia_subido_por_fkey FOREIGN KEY (subido_por) REFERENCES apt.usuario(id)
);
CREATE TABLE apt.ot (
  id bigint NOT NULL DEFAULT nextval('apt.ot_id_seq'::regclass),
  vehiculo_id bigint NOT NULL,
  estado_id bigint,
  descripcion text,
  fecha_apertura timestamp with time zone NOT NULL DEFAULT now(),
  fecha_cierre timestamp with time zone,
  creado_por bigint,
  actualizado_en timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT ot_pkey PRIMARY KEY (id),
  CONSTRAINT ot_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES apt.vehiculo(id),
  CONSTRAINT ot_estado_id_fkey FOREIGN KEY (estado_id) REFERENCES apt.estado(id)
);
CREATE TABLE apt.pausa (
  id bigint NOT NULL DEFAULT nextval('apt.pausa_id_seq'::regclass),
  tarea_id bigint NOT NULL,
  motivo text NOT NULL,
  inicio timestamp with time zone NOT NULL DEFAULT now(),
  fin timestamp with time zone,
  CONSTRAINT pausa_pkey PRIMARY KEY (id),
  CONSTRAINT pausa_tarea_id_fkey FOREIGN KEY (tarea_id) REFERENCES apt.tarea(id)
);
CREATE TABLE apt.repuesto (
  id bigint NOT NULL DEFAULT nextval('apt.repuesto_id_seq'::regclass),
  codigo text UNIQUE,
  descripcion text NOT NULL,
  unidad_medida text NOT NULL DEFAULT 'unidad'::text,
  activo boolean NOT NULL DEFAULT true,
  creado_en timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT repuesto_pkey PRIMARY KEY (id)
);
CREATE TABLE apt.tarea (
  id bigint NOT NULL DEFAULT nextval('apt.tarea_id_seq'::regclass),
  ot_id bigint NOT NULL,
  nombre text NOT NULL,
  estado_id bigint,
  inicio timestamp with time zone,
  fin timestamp with time zone,
  responsable bigint,
  creado_en timestamp with time zone NOT NULL DEFAULT now(),
  actualizado_en timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT tarea_pkey PRIMARY KEY (id),
  CONSTRAINT tarea_ot_id_fkey FOREIGN KEY (ot_id) REFERENCES apt.ot(id),
  CONSTRAINT tarea_estado_id_fkey FOREIGN KEY (estado_id) REFERENCES apt.estado(id)
);
CREATE TABLE apt.tarea_repuesto (
  id bigint NOT NULL DEFAULT nextval('apt.tarea_repuesto_id_seq'::regclass),
  tarea_id bigint NOT NULL,
  repuesto_id bigint NOT NULL,
  cantidad numeric NOT NULL CHECK (cantidad > 0::numeric),
  observacion text,
  creado_en timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT tarea_repuesto_pkey PRIMARY KEY (id),
  CONSTRAINT tarea_repuesto_tarea_id_fkey FOREIGN KEY (tarea_id) REFERENCES apt.tarea(id),
  CONSTRAINT tarea_repuesto_repuesto_id_fkey FOREIGN KEY (repuesto_id) REFERENCES apt.repuesto(id)
);
CREATE TABLE apt.tarea_repuesto_evidencia (
  tarea_repuesto_id bigint NOT NULL,
  evidencia_id bigint NOT NULL,
  CONSTRAINT tarea_repuesto_evidencia_pkey PRIMARY KEY (tarea_repuesto_id, evidencia_id),
  CONSTRAINT tarea_repuesto_evidencia_tarea_repuesto_id_fkey FOREIGN KEY (tarea_repuesto_id) REFERENCES apt.tarea_repuesto(id),
  CONSTRAINT tarea_repuesto_evidencia_evidencia_id_fkey FOREIGN KEY (evidencia_id) REFERENCES apt.evidencia(id)
);
CREATE TABLE apt.usuario (
  id bigint NOT NULL DEFAULT nextval('apt.usuario_id_seq'::regclass),
  nombre text NOT NULL,
  email text,
  rol text NOT NULL DEFAULT 'MECANICO'::text CHECK (rol = ANY (ARRAY['MECANICO'::text, 'SUPERVISOR'::text, 'PORTERIA'::text, 'ADMIN'::text, 'ANALISTA'::text, 'CHOFER'::text, 'GUARDIA'::text])),
  external_id uuid,
  creado_en timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT usuario_pkey PRIMARY KEY (id),
  CONSTRAINT usuario_external_id_fkey FOREIGN KEY (external_id) REFERENCES auth.users(id)
);
CREATE TABLE apt.vehiculo (
  id bigint NOT NULL DEFAULT nextval('apt.vehiculo_id_seq'::regclass),
  patente character varying NOT NULL CHECK (patente::text ~* '^[A-Z]{2}-?[0-9]{4}$'::text OR patente::text ~* '^[A-Z]{4}-?[0-9]{2}$'::text),
  marca text,
  modelo text,
  creado_en timestamp with time zone NOT NULL DEFAULT now(),
  chofer_id bigint,
  CONSTRAINT vehiculo_pkey PRIMARY KEY (id),
  CONSTRAINT vehiculo_chofer_id_fkey FOREIGN KEY (chofer_id) REFERENCES apt.usuario(id)
);
CREATE TABLE apt.vehiculo_patente_hist (
  id bigint NOT NULL DEFAULT nextval('apt.vehiculo_patente_hist_id_seq'::regclass),
  vehiculo_id bigint NOT NULL,
  patente text NOT NULL,
  desde timestamp with time zone NOT NULL DEFAULT now(),
  hasta timestamp with time zone,
  CONSTRAINT vehiculo_patente_hist_pkey PRIMARY KEY (id),
  CONSTRAINT vehiculo_patente_hist_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES apt.vehiculo(id)
);