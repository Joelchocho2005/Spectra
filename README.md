# SPECTRA - Trading Analyzer

SPECTRA es una aplicación Full-Stack de análisis espectral de señales financieras, diseñada para extraer ciclos métricos, evaluar regímenes de mercado y generar señales de inversión a través de técnicas avanzadas de Procesamiento Digital de Señales (DSP).

El proyecto se divide en dos componentes principales:
1. **Frontend**: Interfaz gráfica dinámica desarrollada con React, TypeScript y Vite.
2. **Backend**: API REST de alto rendimiento desarrollada en Python usando FastAPI.

---

## 🛠 Requisitos Previos

Antes de ejecutar el proyecto de forma local, asegúrate de tener instalado:
- [Node.js](https://nodejs.org/es/) (Versión 18 o superior) para correr el frontend.
- [Python](https://www.python.org/downloads/) (Versión 3.9 o superior) para correr el backend.

---

## 🚀 Cómo ejecutar localmente

Para que la aplicación funcione en su totalidad, **se deben correr ambos servidores simultáneamente** utilizando dos terminales separadas.

### 1️⃣ Iniciar la API Backend (FastAPI + Uvicorn)

El backend expone todos los algoritmos matemáticos y las conexiones de datos a las que el frontend consultará. Todo el código vive dentro de la carpeta `backend/`.

**Paso a paso:**
1. Abre tu primera terminal.
2. Navega a la carpeta del backend:
   ```bash
   cd backend
   ```
3. *(Recomendado)* Crea y activa un entorno virtual de Python.
   - **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
4. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
5. Inicia el servidor de desarrollo utilizando **Uvicorn**:
   ```bash
   uvicorn app.main:app --reload
   ```
   > 📌 **¿Qué hace este comando?** Levanta el backend en el puerto `8000`. La etiqueta `--reload` hace que si realizas cambios en el código de Python, el servidor se reinicie automáticamente sin que tengas que hacerlo a mano.

El backend estará disponible en: [http://localhost:8000](http://localhost:8000)
La documentación autogenerada de la API interactiva (Swagger UI) está en: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2️⃣ Iniciar el Frontend (React + Vite)

El frontend contiene la interfaz de usuario con la que se interactúa directamente. Todo el código del frontend vive dentro de la carpeta `frontend/`.

**Paso a paso:**
1. Abre una **segunda terminal**.
2. Navega a la carpeta del frontend:
   ```bash
   cd frontend
   ```
3. Instala las dependencias y paquetes de Node:
   ```bash
   npm install
   ```
4. Inicia el servidor de desarrollo de **Vite**:
   ```bash
   npm run dev
   ```
   > 📌 Vite compilará tu aplicación en tiempo real y abrirá un servidor local super rápido gracias a Hot Module Replacement (HMR).

El frontend estará disponible en: [http://localhost:5173](http://localhost:5173)

---

## 📦 Comandos de Despliegue a Producción (Deploy)

Si en el futuro deseas subir la página a internet (servidores como Render, Vercel, Railway, etc.), estos son los comandos exactos que se usan en entornos de producción:

### Despliegue del Backend
En producción **NUNCA** se usa la bandera `--reload` ya que consume recursos innecesarios. El comando estricto de despliegue para **Uvicorn** es:
```bash
# Generalmente acompañado por Gunicorn para estabilizar los procesos (workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Despliegue del Frontend
Vite empaqueta toda la aplicación en archivos HTML/CSS/JS puros y comprimidos, borrando todo rastro de código no utilizado e ignorando el TypeScript.

1. Se genera la build de producción:
   ```bash
   npm run build
   ```
2. Esto creará una carpeta llamada `dist/` en tu proyecto. Esos son los archivos estáticos listos para ser alojados en cualquier servidor Apache, Nginx o servicios gratis como **Vercel** o **Netlify**.
3. Para previsualizar cómo quedó empaquetado para producción, puedes usar:
   ```bash
   npm run preview
   ```
