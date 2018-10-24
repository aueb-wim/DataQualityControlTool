# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /
WORKDIR /

# Copy the current directory contents into the container at /app
COPY qctool/qctab.py /

COPY requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN ls

