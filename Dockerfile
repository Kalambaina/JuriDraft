# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 7860 (Gradio default)
EXPOSE 7860

# Run the app with uvicorn (adjust module name if needed)
CMD ["uvicorn", "main:lexidraft_ui", "--host", "0.0.0.0", "--port", "7860"]
