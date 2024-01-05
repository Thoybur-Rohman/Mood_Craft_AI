# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for OpenCV and Tkinter
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libx11-6 libxext-dev libxrender-dev \
    libxinerama-dev libxi-dev libxrandr-dev libxcursor-dev libxtst-dev tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Clear Python bytecode cache (optional, helps resolve some issues)
RUN find /usr/local/lib/python3.8/ -type d -name __pycache__ -exec rm -r {} + && \
    find /usr/local/lib/python3.8/ -type f -name "*.pyc" -exec rm -f {} +

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# Force reinstall matplotlib to avoid EOFError
RUN pip install --no-cache-dir --force-reinstall matplotlib
RUN pip install --no-cache-dir -r requirements.txt

# Run main_app.py when the container launches
CMD ["python", "main_app.py"]

