import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """Abre una conexión con MySQL local usando los valores del archivo .env."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "helpdesk_ti"),
    )


def ejecutar_consulta(sql, parametros=None, obtener_resultados=False):
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, parametros or ())
        if obtener_resultados:
            return cursor.fetchall()
        conexion.commit()
        return cursor.lastrowid
    except Error as exc:
        if conexion:
            conexion.rollback()
        raise RuntimeError(f"MySQL: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def listar_usuarios():
    return ejecutar_consulta(
        "SELECT id_usuario, nombre FROM usuarios ORDER BY nombre",
        obtener_resultados=True,
    )


def listar_tecnicos():
    return ejecutar_consulta(
        "SELECT id_tecnico, nombre FROM tecnicos WHERE activo = TRUE ORDER BY nombre",
        obtener_resultados=True,
    )


def listar_tickets(busqueda="", estado="Todos"):
    sql = """
        SELECT t.id_ticket, t.titulo, t.descripcion, t.prioridad, t.estado,
               t.id_usuario, t.id_tecnico, u.nombre AS usuario, te.nombre AS tecnico
        FROM tickets t
        INNER JOIN usuarios u ON u.id_usuario = t.id_usuario
        LEFT JOIN tecnicos te ON te.id_tecnico = t.id_tecnico
        WHERE (
            %s = '' OR LOWER(t.titulo) LIKE %s
            OR LOWER(u.nombre) LIKE %s OR LOWER(t.estado) LIKE %s
        )
    """
    termino = f"%{busqueda.lower()}%"
    parametros = [busqueda, termino, termino, termino]
    if estado and estado != "Todos":
        sql += " AND t.estado = %s"
        parametros.append(estado)
    sql += " ORDER BY t.id_ticket DESC"
    return ejecutar_consulta(sql, parametros, obtener_resultados=True)


def crear_ticket(titulo, descripcion, prioridad, id_usuario, id_tecnico=None):
    if id_tecnico is None:
        return ejecutar_consulta(
            """CALL sp_registrar_ticket(%s, %s, %s, %s, NULL)""",
            (titulo, descripcion, prioridad, id_usuario),
        )
    return ejecutar_consulta(
        """CALL sp_registrar_ticket(%s, %s, %s, %s, %s)""",
        (titulo, descripcion, prioridad, id_usuario, id_tecnico),
    )


def actualizar_ticket(id_ticket, titulo, descripcion, prioridad, id_usuario, id_tecnico=None, estado=None):
    if estado is None:
        ejecutar_consulta(
            """UPDATE tickets
               SET titulo=%s, descripcion=%s, prioridad=%s, id_usuario=%s, id_tecnico=%s
               WHERE id_ticket=%s""",
            (titulo, descripcion, prioridad, id_usuario, id_tecnico, id_ticket),
        )
    else:
        ejecutar_consulta(
            """UPDATE tickets
               SET estado=%s
               WHERE id_ticket=%s""",
            (estado, id_ticket),
        )


def eliminar_ticket(id_ticket):
    # El historial debe eliminarse antes por la clave foránea.
    ejecutar_consulta("DELETE FROM historial_tickets WHERE id_ticket = %s", (id_ticket,))
    ejecutar_consulta("DELETE FROM tickets WHERE id_ticket = %s", (id_ticket,))


def listar_historial():
    return ejecutar_consulta(
        """SELECT id_historial, id_ticket, estado_anterior, estado_nuevo, fecha_cambio
           FROM historial_tickets ORDER BY id_historial DESC LIMIT 30""",
        obtener_resultados=True,
    )


def obtener_resumen():
    filas = ejecutar_consulta(
        """SELECT COUNT(*) AS total,
                  SUM(estado='Pendiente') AS pendientes,
                  SUM(estado='En proceso') AS en_proceso,
                  SUM(estado='Resuelto') AS resueltos
           FROM tickets""",
        obtener_resultados=True,
    )
    fila = filas[0]
    return {k: int(fila[k] or 0) for k in ("total", "pendientes", "en_proceso", "resueltos")}
