# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# --- ADD THIS LINE HERE ---
# Set the timezone to UTC to ensure all datetime operations are consistent
ENV TZ=Etc/UTC

# Install the CORRECT system dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    file \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy your project's dependencies list
COPY requirements.txt .

# Install the Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend code into the container
COPY . .

# Tell Docker to make port 5000 available
# Note: Your original file exposed 5000, not 5001.
EXPOSE 5000

# The command to run when the container starts
CMD ["python", "-m", "flask", "--app", "src/main.py", "run", "--debug", "--host=0.0.0.0"]