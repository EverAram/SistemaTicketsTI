# Sistema de Tickets de Soporte TI

Aplicación de escritorio hecha con Python, Flet y MySQL para registrar y administrar solicitudes de soporte técnico.

## Funcionalidades

- Crear, editar y eliminar tickets.
- Buscar por título, usuario o estado.
- Filtrar por estado.
- Asignar usuario y técnico.
- Resumen de tickets por estado.
- Historial de cambios de estado mediante trigger MySQL.
- Registro de tickets mediante el procedimiento almacenado `sp_registrar_ticket`.
- Consultas con `JOIN` para mostrar los nombres del usuario y del técnico.

## Requisitos

- Python 3.10 o superior.
- MySQL Server en ejecución.
- Base de datos `helpdesk_ti` con las tablas, trigger y procedimiento del proyecto.

## Instalación

1. Clona o descarga el repositorio.
2. Abre una terminal en la carpeta del proyecto.
3. Crea y activa un entorno virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Instala las dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

5. Edita `.env` y coloca tu contraseña real de MySQL en `DB_PASSWORD`.
6. Ejecuta la aplicación:

   ```powershell
   python app.py
   ```

## Seguridad

No publiques el archivo `.env` ni contraseñas. En GitHub se debe subir `.env.example`, no el `.env` real.

## Base de datos

La aplicación utiliza la base `helpdesk_ti` en `localhost:3306`. El script SQL con las tablas, el trigger y el procedimiento debe guardarse en el repositorio para que otra persona pueda recrear la base.
