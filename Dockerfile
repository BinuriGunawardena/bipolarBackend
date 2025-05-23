# # Use an official Python runtime as the base image
# FROM python:3.9-slim

# # Set working directory
# WORKDIR /app

# # Copy requirements file
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application
# COPY . .

# # Set environment variables
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0

# # Expose port 5000
# EXPOSE 5000

# # Run the application
# CMD ["flask", "run"]

# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variable for port (used by Gunicorn)
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
