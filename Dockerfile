# Use an official Python runtime as a parent image
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /app/

# Set Pythonpath for gunicorn to be able to find wsgi app object
ENV PYTHONPATH=/app

# Run collectstatic to gather static files
RUN python3 Django/manage.py collectstatic --noinput

# Expose the port that the Django app will run on
EXPOSE 8000

# Run the Django app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "imaginglab.wsgi:application"]