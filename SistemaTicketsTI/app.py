import flet as ft
from database import (
    listar_tickets, listar_usuarios, listar_tecnicos, listar_historial,
    crear_ticket, actualizar_ticket, eliminar_ticket, obtener_resumen
)


def main(page: ft.Page):
    page.title = "Sistema de Tickets de Soporte TI"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    mensaje = ft.Text()
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Título")),
            ft.DataColumn(ft.Text("Prioridad")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Usuario")),
            ft.DataColumn(ft.Text("Técnico")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
        column_spacing=18,
        heading_row_height=42,
        data_row_min_height=48,
    )

    campo_busqueda = ft.TextField(
        label="Buscar por título, usuario o estado",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
    )
    filtro_estado = ft.Dropdown(
        label="Filtrar estado",
        width=190,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("En proceso"),
            ft.dropdown.Option("Resuelto"),
            ft.dropdown.Option("Cerrado"),
        ],
        value="Todos",
    )

    titulo = ft.TextField(label="Título", expand=True)
    descripcion = ft.TextField(label="Descripción", multiline=True, min_lines=2, max_lines=4)
    prioridad = ft.Dropdown(
        label="Prioridad",
        value="Media",
        options=[ft.dropdown.Option(x) for x in ["Baja", "Media", "Alta", "Urgente"]],
    )
    usuario = ft.Dropdown(label="Usuario", expand=True, options=[])
    tecnico = ft.Dropdown(label="Técnico (opcional)", expand=True, options=[], value="")

    resumen = ft.Row(wrap=True, spacing=12)

    def avisar(texto, error=False):
        mensaje.value = texto
        mensaje.color = ft.Colors.RED if error else ft.Colors.GREEN
        page.update()

    def cargar_opciones():
        try:
            usuario.options = [
                ft.dropdown.Option(str(u["id_usuario"]), f'{u["nombre"]} (ID {u["id_usuario"]})')
                for u in listar_usuarios()
            ]
            tecnico.options = [ft.dropdown.Option("", "Sin asignar")] + [
                ft.dropdown.Option(str(t["id_tecnico"]), f'{t["nombre"]} (ID {t["id_tecnico"]})')
                for t in listar_tecnicos()
            ]
        except Exception as ex:
            avisar(f"Error cargando opciones desde la BD: {ex}", True)

    def actualizar_resumen():
        try:
            datos = obtener_resumen()
            resumen.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Text(etiqueta, size=13, color=ft.Colors.GREY_700),
                        ft.Text(str(valor), size=25, weight=ft.FontWeight.BOLD),
                    ], spacing=4),
                    padding=16,
                    border_radius=12,
                    bgcolor=ft.Colors.BLUE_50,
                    width=180,
                )
                for etiqueta, valor in [
                    ("Total tickets", datos.get("total", 0)),
                    ("Pendientes", datos.get("pendientes", 0)),
                    ("En proceso", datos.get("en_proceso", 0)),
                    ("Resueltos", datos.get("resueltos", 0)),
                ]
            ]
        except Exception as ex:
            print(f"Error resumen: {ex}")

    def editar_ticket(ticket):
        titulo.value = ticket["titulo"]
        descripcion.value = ticket["descripcion"]
        prioridad.value = ticket["prioridad"]
        usuario.value = str(ticket["id_usuario"])
        tecnico.value = "" if ticket["id_tecnico"] is None else str(ticket["id_tecnico"])
        boton_guardar.text = "Guardar cambios"
        boton_guardar.data = ticket["id_ticket"]
        avisar(f'Editando ticket #{ticket["id_ticket"]}. Completa los cambios y guarda.')

    def limpiar_formulario(e=None):
        titulo.value = ""
        descripcion.value = ""
        prioridad.value = "Media"
        usuario.value = None
        tecnico.value = ""
        boton_guardar.text = "Crear ticket"
        boton_guardar.data = None
        page.update()

    def guardar_ticket(e):
        try:
            if not titulo.value or not titulo.value.strip():
                raise ValueError("El título es obligatorio.")
            if not descripcion.value or not descripcion.value.strip():
                raise ValueError("La descripción es obligatoria.")
            if not usuario.value:
                raise ValueError("Selecciona un usuario.")
            if boton_guardar.data:
                actualizar_ticket(
                    int(boton_guardar.data), titulo.value.strip(), descripcion.value.strip(),
                    prioridad.value, int(usuario.value),
                    int(tecnico.value) if tecnico.value else None,
                )
                avisar("Ticket actualizado correctamente.")
            else:
                crear_ticket(
                    titulo.value.strip(), descripcion.value.strip(), prioridad.value,
                    int(usuario.value), int(tecnico.value) if tecnico.value else None,
                )
                avisar("Ticket creado correctamente.")
            limpiar_formulario()
            refrescar()
        except Exception as ex:
            avisar(f"No se pudo guardar: {ex}", True)

    def confirmar_eliminar(ticket):
        def borrar(e):
            try:
                eliminar_ticket(ticket["id_ticket"])
                dialog.open = False
                page.update()
                avisar(f'Ticket #{ticket["id_ticket"]} eliminado.')
                refrescar()
            except Exception as ex:
                dialog.open = False
                page.update()
                avisar(f"No se pudo eliminar: {ex}", True)

        def cerrar_dialogo(e=None):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar ticket"),
            content=ft.Text(f'¿Seguro que quieres eliminar el ticket #{ticket["id_ticket"]}: {ticket["titulo"]}?'),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.TextButton("Eliminar", on_click=borrar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def cambiar_estado(ticket, nuevo_estado):
        try:
            actualizar_ticket(
                ticket["id_ticket"], ticket["titulo"], ticket["descripcion"],
                ticket["prioridad"], ticket["id_usuario"], ticket["id_tecnico"],
                estado=nuevo_estado,
            )
            avisar(f'Ticket #{ticket["id_ticket"]}: estado cambiado a "{nuevo_estado}".')
            refrescar()
        except Exception as ex:
            avisar(f"No se pudo cambiar el estado: {ex}", True)

    def refrescar(e=None):
        try:
            q = (campo_busqueda.value or "").strip().lower()
            estado = filtro_estado.value or "Todos"
            tickets = listar_tickets(q, estado)
            tabla.rows = []
            for t in tickets:
                selector_estado = ft.Dropdown(
                    value=t["estado"],
                    width=130,
                    dense=True,
                    options=[ft.dropdown.Option(x) for x in ["Pendiente", "En proceso", "Resuelto", "Cerrado"]],
                )
                selector_estado.on_change = lambda e, ticket=t: cambiar_estado(ticket, e.control.value)

                tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(t["id_ticket"]))),
                        ft.DataCell(ft.Text(t["titulo"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(t["prioridad"])),
                        ft.DataCell(selector_estado),
                        ft.DataCell(ft.Text(t["usuario"])),
                        ft.DataCell(ft.Text(t["tecnico"] or "Sin asignar")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT, tooltip="Editar", on_click=lambda e, ticket=t: editar_ticket(ticket)),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", on_click=lambda e, ticket=t: confirmar_eliminar(ticket)),
                        ], spacing=0)),
                    ])
                )
            actualizar_resumen()
            historial.controls = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY),
                    title=ft.Text(f'Ticket #{h["id_ticket"]}: {h["estado_anterior"] or "Nuevo"} → {h["estado_nuevo"]}'),
                    subtitle=ft.Text(str(h["fecha_cambio"])),
                )
                for h in listar_historial()
            ]
            page.update()
        except Exception as ex:
            avisar(f"Error al cargar datos desde la BD: {ex}", True)

    boton_guardar = ft.Button("Crear ticket", icon=ft.Icons.SAVE, on_click=guardar_ticket)
    boton_limpiar = ft.Button("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_formulario)
    boton_buscar = ft.Button("Buscar / actualizar", icon=ft.Icons.SEARCH, on_click=refrescar)
    
    historial = ft.Column(spacing=0)

    cargar_opciones()
    page.add(
        ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Sistema de Tickets TI", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Gestión de solicitudes de soporte técnico", color=ft.Colors.GREY_700),
                ], expand=True),
                ft.Icon(ft.Icons.HEADSET_MIC, size=42, color=ft.Colors.BLUE_700),
            ]),
            resumen,
            ft.Divider(),
            ft.Text("Crear o editar ticket", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([titulo, prioridad], vertical_alignment=ft.CrossAxisAlignment.START),
            descripcion,
            ft.Row([usuario, tecnico], vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                boton_guardar,
                boton_limpiar,
            ]),
            mensaje,
            ft.Divider(),
            ft.Text("Tickets registrados", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                campo_busqueda,
                filtro_estado,
                boton_buscar,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO),
            ft.Divider(),
            ft.Text("Historial de cambios", size=20, weight=ft.FontWeight.BOLD),
            historial,
        ], spacing=14)
    )
    refrescar()


if __name__ == "__main__":
    ft.run(main)