
# Use an official Python runtime as a parent image
FROM python:3.12-slim as backend

# Set the working directory in the container
WORKDIR /app

# Copy the backend requirements file into the container
COPY app/requirements.txt .

# Install backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code into the container
COPY app/ .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the backend port
EXPOSE 8000

# Command to run the FastAPI server
CMD ["fastapi", "run"]

# Use an official Node.js runtime as a parent image
FROM node:18-alpine as frontend

# Set the working directory in the container
WORKDIR /askpod

# Copy the frontend package.json and package-lock.json into the container
COPY askpod/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the frontend source code into the container
COPY askpod/ .

# Expose the frontend port
EXPOSE 3000

# Command to run the Next.js development server
CMD ["npm", "run", "dev"]
