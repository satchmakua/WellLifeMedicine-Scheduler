# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the app folder contents into the container at /usr/src/app
COPY app/ /usr/src/app/

# Copy the templates directory into the container
COPY templates/ /usr/src/app/templates/

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable and ensure it's pointing to the correct directory
ENV FLASK_APP=route.py

# Run route.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
