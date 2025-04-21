# Imagen base de Python
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema necesarias
RUN apt-get update && apt-get install -y gcc libmariadb-dev-compat libmariadb-dev

# Copiar solo el requirements.txt primero
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto de la aplicación (FastAPI usa 8000)
EXPOSE 8000

# Comando para ejecutar la app con Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
