# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py makemigrations evaluation_tool

# Expose port 8000 for the Django app to run on
EXPOSE 8000

# Load environment variables from .env file
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
