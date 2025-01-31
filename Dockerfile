# Use a lightweight Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy everything to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 7860 (default HF Spaces port)
EXPOSE 7860

# Run the Flask app
CMD ["python", "app.py"]
