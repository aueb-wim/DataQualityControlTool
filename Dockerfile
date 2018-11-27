# Use an official Python runtime as a parent image
FROM python:3.7-alpine3.8

# Set the working directory to /
WORKDIR /

# Copy the current directory contents into the container at /app
COPY mipqctool/ /mipqctool
COPY setup.py requirements.txt README.md install.sh /

# install texlive LaTex compiler
RUN apk add texlive

###### Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# install the mipqctool
RUN sh install.sh
