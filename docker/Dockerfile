# Use the official Kali Linux image as the base
FROM kalilinux/kali-rolling

# Update and install additional packages
RUN apt-get update && \
    apt-get install -y kali-tools-top10 && \
    rm -rf /var/lib/apt/lists/*
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get install -y python3-pip
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Make sure the script is executable
RUN chmod +x app.py

# Expose a port if your application listens on one (e.g., 80 for web applications)
# EXPOSE 80

# Define environment variables if needed
ENV PYTHONUNBUFFERED=1

# Run the Python script when the container launches
CMD ["python3", "app.py"]

# Set the default command to run when the container starts
# CMD ["/bin/bash"]
