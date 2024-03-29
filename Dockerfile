# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt update && \
    apt install -y libgl1-mesa-glx libglib2.0-0 && \
    apt clean

# Set the LD_LIBRARY_PATH environment variable
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
# Copy the requirements file and install Python dependencies
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port on which your Flask app runs
EXPOSE 5000

# Command to run the Flask application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]

