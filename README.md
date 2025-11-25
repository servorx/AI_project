# README - Asistente Comercial (fast Api + Qdrant + Langroid)

## Descripción

Este proyecto es un asistente comercial que utiliza la tecnología de inteligencia artificial para proporcionar respuestas personalizadas a los clientes. El asistente utiliza una base de datos de conocimientos (KB) para obtener información relevante y proporcionar respuestas precisas y útiles.

## Tecnologías

- FastAPI: Framework de desarrollo web rápido y sencillo para Python.
- Qdrant: Base de datos de vectores de alta precisión y escalabilidad.
- Langroid: Framework de inteligencia artificial para Python.
- Gemini: API de generación de texto.

## Estructura del proyecto

El proyecto está dividido en dos partes principales:

- **Backend**: Contiene el código de la aplicación de backend, que se encarga de procesar las solicitudes del cliente y proporcionar respuestas útiles.
- **Frontend**: Contiene el código de la aplicación de frontend, que se encarga de mostrar la interfaz de usuario y recibir las solicitudes del cliente.

## Requisitos

Para ejecutar el proyecto, es necesario tener instalados los siguientes paquetes:

- Python 3.10 o superior.
- FastAPI.
- Qdrant.
- Langroid.
- Gemini.

## Instalación

Para instalar los paquetes necesarios, sigue estos pasos:

1. Abre una terminal o línea de comandos y ejecuta los siguientes comandos para clonar y abrir el proyecto:

```bash
git clone https://github.com/servorx/AI_project.git
cd AI_project
code .
```
2. Crea el entorno de desarrollo: 
```bash
cd backend  
python3 -m venv .venv
source .venv/bin/activate
```

3 . Ejecuta el siguiente comando para instalar los paquetes necesarios:

```bash
pip install -r requirements.txt
```

Esto instalará todos los paquetes necesarios para ejecutar el proyecto.
Ahora, para ejecutar el proyecto, sigue estos pasos:

4. Ejecuta el siguiente comando para iniciar el servidor de FastAPI:

```bash
uvicorn app.main:app --reload
```

5. Abre un navegador web y acceda a la URL http://127.0.0.1:8000/docs para acceder a la documentación de la API.

6. Para iniciar el cliente de la aplicación, abre un navegador web y acceda a la URL http://127.0.0.1:5173.

7. En el cliente, ingresa el nombre de usuario y contraseña para acceder a la aplicación.