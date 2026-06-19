# Use official Python image
FROM python:3.10-slim

# Set the working directory inside the server
WORKDIR /app

# Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your Python files, the database, and the logo
COPY . .

# Hugging Face requires apps to run on port 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
