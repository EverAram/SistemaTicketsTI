CREATE DATABASE IF NOT EXISTS helpdesk_ti;
USE helpdesk_ti;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS perfiles_usuario (
    id_perfil INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    telefono VARCHAR(20),
    departamento VARCHAR(100),
    CONSTRAINT fk_perfil_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS tecnicos (
    id_tecnico INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS especialidades (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tecnico_especialidad (
    id_tecnico INT NOT NULL,
    id_especialidad INT NOT NULL,
    PRIMARY KEY (id_tecnico, id_especialidad),
    CONSTRAINT fk_tecesp_tecnico FOREIGN KEY (id_tecnico) REFERENCES tecnicos(id_tecnico),
    CONSTRAINT fk_tecesp_especialidad FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
);

CREATE TABLE IF NOT EXISTS tickets (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    prioridad ENUM('Baja', 'Media', 'Alta', 'Urgente') NOT NULL DEFAULT 'Media',
    estado ENUM('Pendiente', 'En proceso', 'Resuelto', 'Cerrado') NOT NULL DEFAULT 'Pendiente',
    id_usuario INT NOT NULL,
    id_tecnico INT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_ticket_tecnico FOREIGN KEY (id_tecnico) REFERENCES tecnicos(id_tecnico)
);

CREATE TABLE IF NOT EXISTS historial_tickets (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_ticket INT NOT NULL,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_historial_ticket FOREIGN KEY (id_ticket) REFERENCES tickets(id_ticket)
);

DROP TRIGGER IF EXISTS trg_historial_estado_ticket;
DELIMITER //
CREATE TRIGGER trg_historial_estado_ticket
AFTER UPDATE ON tickets
FOR EACH ROW
BEGIN
    IF NOT (OLD.estado <=> NEW.estado) THEN
        INSERT INTO historial_tickets (id_ticket, estado_anterior, estado_nuevo)
        VALUES (NEW.id_ticket, OLD.estado, NEW.estado);
    END IF;
END//
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_registrar_ticket;
DELIMITER //
CREATE PROCEDURE sp_registrar_ticket(
    IN p_titulo VARCHAR(150),
    IN p_descripcion TEXT,
    IN p_prioridad VARCHAR(20),
    IN p_id_usuario INT,
    IN p_id_tecnico INT
)
BEGIN
    IF p_titulo IS NULL OR TRIM(p_titulo) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El titulo es obligatorio';
    END IF;
    IF p_descripcion IS NULL OR TRIM(p_descripcion) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La descripcion es obligatoria';
    END IF;
    IF p_prioridad NOT IN ('Baja', 'Media', 'Alta', 'Urgente') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prioridad no valida';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM usuarios WHERE id_usuario = p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no existe';
    END IF;
    IF p_id_tecnico IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM tecnicos WHERE id_tecnico = p_id_tecnico AND activo = TRUE
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tecnico no existe o esta inactivo';
    END IF;
    INSERT INTO tickets (titulo, descripcion, prioridad, id_usuario, id_tecnico)
    VALUES (TRIM(p_titulo), p_descripcion, p_prioridad, p_id_usuario, p_id_tecnico);
END//
DELIMITER ;

-- Datos de ejemplo opcionales. Ejecuta este bloque solo una vez si quieres datos iniciales.
-- INSERT INTO usuarios (nombre, correo) VALUES ('Juan Pérez', 'juan@ejemplo.cl'), ('María González', 'maria@ejemplo.cl');
-- INSERT INTO perfiles_usuario (id_usuario, telefono, departamento) VALUES (1, '912345678', 'Administración'), (2, '987654321', 'Contabilidad');
-- INSERT INTO tecnicos (nombre, correo) VALUES ('Carlos Soto', 'carlos@ejemplo.cl'), ('Ana Torres', 'ana@ejemplo.cl');
-- INSERT INTO especialidades (nombre) VALUES ('Redes'), ('Hardware'), ('Software');
-- INSERT INTO tecnico_especialidad (id_tecnico, id_especialidad) VALUES (1, 1), (1, 2), (2, 3);
