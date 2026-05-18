# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
# Set the working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt ./

# Install dependencies (Using CPU version of PyTorch to save space)
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the application code
COPY . ./

# Expose the port Uvicorn will run on
EXPOSE 5000

# Run the web service on container startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
