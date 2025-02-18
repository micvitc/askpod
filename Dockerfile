# Use an official Python runtime as a parent image
FROM python:3.12-slim

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

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set the working directory for the frontend
WORKDIR /askpod

# Copy the frontend package.json and package-lock.json into the container
COPY askpod/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the frontend source code into the container
COPY askpod/ .

# Expose the ports
EXPOSE 8000 3000

# Command to run both the FastAPI server and Next.js development server
CMD ["sh", "-c", "cd /app && fastapi run & cd /askpod && npm run dev"]
