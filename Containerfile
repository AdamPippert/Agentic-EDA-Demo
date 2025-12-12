# Dockerfile

# Use a lightweight official Python image as the base
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY agent.py .

# Expose the port where LangServe/FastAPI is running
EXPOSE 8080

# Command to run the application using a production-ready server (e.g., Gunicorn + Uvicorn workers)
# The OPENAI_API_KEY and other credentials should be passed as environment variables 
# during deployment on OpenShift.
CMD ["gunicorn", "agent:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
