# Use an official Python runtime as a parent image
FROM iosifsp/qclibs:0.0.1

# Set the working directory to /
WORKDIR /

# Copy the current directory contents into the container at /app
COPY qctool/qctab.py /qctab.py


CMD ["python3", "qctab.py", "--input_csv", "/input/edsd_merge.csv", "--meta_csv", "/input/metadata.csv", "Subject Code"]
