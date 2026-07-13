# Use a slim Python image to reduce size
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the pre-built vector database
COPY main.py .
COPY vector_db/ ./vector_db/

# Expose the API port
EXPOSE 8000

# Command to run the API
CMD ["python", "main.py"]