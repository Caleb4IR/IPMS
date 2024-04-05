# Use an official Python runtime as a parent image
FROM python:3.8-slim
 
# Set the working directory in the container
WORKDIR /usr/src/app
 
# Install system dependencies for PyODBC and MSSQL ODBC Driver
RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg g++ unixodbc-dev wget \
    && wget -O- https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && wget https://packages.microsoft.com/config/debian/10/prod.list -O /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    # Clean up the cache and temporary files
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
 
# Copy the current directory contents into the container at /usr/src/app
COPY . .
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Make port 8000 available to the world outside this container
EXPOSE 8000
 
# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
 
# Run app.py using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]