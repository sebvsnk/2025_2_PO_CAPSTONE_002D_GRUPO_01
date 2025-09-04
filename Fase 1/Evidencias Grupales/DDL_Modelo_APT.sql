-- DDL Modelo de Datos – APT PepsiCo (neutral SQL)
-- Nota: ajuste de sintaxis puede ser necesario según motor (PostgreSQL/MySQL/SQL Server).

CREATE TABLE Usuario (
  idUsuario       VARCHAR(36) PRIMARY KEY,
  nombre          VARCHAR(120) NOT NULL,
  email           VARCHAR(160) NOT NULL UNIQUE,
  hashPassword    VARCHAR(255) NOT NULL,
  creadoEn        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Rol (
  idRol           VARCHAR(36) PRIMARY KEY,
  nombre          VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE UsuarioRol (
  idUsuario       VARCHAR(36) NOT NULL,
  idRol           VARCHAR(36) NOT NULL,
  PRIMARY KEY (idUsuario, idRol),
  FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario),
  FOREIGN KEY (idRol) REFERENCES Rol(idRol)
);

CREATE TABLE Vehiculo (
  idVehiculo      VARCHAR(36) PRIMARY KEY,
  patente         VARCHAR(10) NOT NULL UNIQUE,
  tipo            VARCHAR(40),
  estado          VARCHAR(40),
  creadoEn        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE OT (
  idOT            VARCHAR(36) PRIMARY KEY,
  idVehiculo      VARCHAR(36) NOT NULL,
  fechaApertura   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fechaCierre     TIMESTAMP NULL,
  estado          VARCHAR(30) NOT NULL,
  FOREIGN KEY (idVehiculo) REFERENCES Vehiculo(idVehiculo)
);

CREATE TABLE Tarea (
  idTarea         VARCHAR(36) PRIMARY KEY,
  idOT            VARCHAR(36) NOT NULL,
  nombre          VARCHAR(120) NOT NULL,
  estado          VARCHAR(30) NOT NULL,
  inicio          TIMESTAMP NULL,
  fin             TIMESTAMP NULL,
  FOREIGN KEY (idOT) REFERENCES OT(idOT)
);

CREATE TABLE Pausa (
  idPausa         VARCHAR(36) PRIMARY KEY,
  idTarea         VARCHAR(36) NOT NULL,
  motivo          VARCHAR(140) NOT NULL,
  inicio          TIMESTAMP NOT NULL,
  fin             TIMESTAMP NULL,
  FOREIGN KEY (idTarea) REFERENCES Tarea(idTarea)
);

CREATE TABLE Evidencia (
  idEvidencia     VARCHAR(36) PRIMARY KEY,
  idTarea         VARCHAR(36) NOT NULL,
  url             VARCHAR(512) NOT NULL,
  tipo            VARCHAR(40) NOT NULL,
  tamanoBytes     BIGINT,
  usuario         VARCHAR(160) NOT NULL,
  fecha           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (idTarea) REFERENCES Tarea(idTarea)
);

CREATE TABLE BitacoraPorteria (
  id              VARCHAR(36) PRIMARY KEY,
  idVehiculo      VARCHAR(36) NOT NULL,
  fecha           DATE NOT NULL,
  hora            TIME NOT NULL,
  tipo            VARCHAR(10) NOT NULL, -- 'entrada' | 'salida'
  usuario         VARCHAR(160) NOT NULL,
  FOREIGN KEY (idVehiculo) REFERENCES Vehiculo(idVehiculo)
);

CREATE TABLE Auditoria (
  id              VARCHAR(36) PRIMARY KEY,
  usuario         VARCHAR(160) NOT NULL,
  accion          VARCHAR(60) NOT NULL,
  objeto          VARCHAR(120) NOT NULL,
  fecha           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  detalle         VARCHAR(500)
);

-- Índices sugeridos
CREATE INDEX idx_vehiculo_patente ON Vehiculo(patente);
CREATE INDEX idx_bitacora_fecha ON BitacoraPorteria(fecha);
CREATE INDEX idx_tarea_ot ON Tarea(idOT);
CREATE INDEX idx_pausa_tarea ON Pausa(idTarea);
CREATE INDEX idx_evidencia_tarea ON Evidencia(idTarea);

-- Reglas/Checks (ajustar a motor)
-- CHECK: motivo de pausa not null; patente patrón configurable; tipo de evidencia permitido; transiciones de estado validar en capa de aplicación.

