# Dicom Converter

This is a simple Streamlit app that allows you to convert DICOM files to FHIR resources.

## Description

The DICOM Converter is a web application built with Streamlit that enables users to:
- Upload and view DICOM medical imaging files
    - NB: This `.dcm` files were gotten from [kaggle](https://www.kaggle.com/datasets/trainingdatapro/computed-tomography-ct-of-the-brain)
- Convert DICOM metadata to FHIR resources
- Visualize DICOM images
- Export FHIR resources in CSV format

## System Requirements

### Hardware Requirements
- CPU: 2+ cores recommended
- RAM: Minimum 4GB, 8GB recommended
- Disk Space: At least 2GB free space

### Software Requirements
- Python 3.10+
- Docker Engine 20.10.x or newer
- Docker Compose v2.x or newer
- Operating System:
  - Linux (recommended)
  - macOS 10.15 or newer
  - Windows 10/11 with WSL2

## Dependencies

- Streamlit
- Pandas
- Pydicom
- Pillow
- Matplotlib
- Numpy
- FHIRpy

## Installation and Setup

### Local Setup

1. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
2. Clone the repository:
    ```bash
    git clone https://github.com/EthelEz/DicomFhirConverter.git
    cd DicomFhirConverter
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a `.env` file with the following variables:
    ```bash
    local_url="http://localhost:8090/fhir"
    ```
5. Run Docker Compose to start Docker containers:
    ```bash
    docker-compose up
    ```
6. Run the application:
    ```bash
    streamlit run app.py
    ```

### Docker Setup

1. Build and run using Docker Compose:
    ```bash
    streamlit-compose up --build
    ```
    This creates:
    - Streamlit container (http://localhost:8501)
    - HAPI FHIR server (http://localhost:8090/fhir)

2. Stop services:
    ```bash
    docker-compose down
    ```

## Docker Image Build Process

### Base Image
The application uses a multi-stage build process using `Dockerfile` and `streamlit-compose.yaml`.

### Build Arguments
- `PYTHON_VERSION`: Python version (default: 3.10)
- `PORT`: Application port (default: 8501)
- `FHIR_SERVER_URL`: FHIR server URL (default: http://localhost:8090/fhir)
- `FHIR_SERVER_PORT`: FHIR server port (default: 8090)
- `FHIR_SERVER_PATH`: FHIR server path (default: /fhir)


### Application Settings
- `config.yaml` for Streamlit configuration:
  ```yaml
  server:
    port: 8501
    address: 0.0.0.0
  ```

## Troubleshooting

### Common Issues

1. **Docker Connection Issues**
   ```bash
   # Check if Docker daemon is running
   docker info
   # Check container status
   docker-compose ps
   ```

2. **FHIR Server Connection**
   - Verify FHIR server is running: `curl http://localhost:8090/fhir/metadata`
   - Check network connectivity between containers

3. **Memory Issues**
   - Increase Docker memory limit in Docker Desktop settings
   - Check system memory usage: `free -h`

### Logs
- Access container logs:
  ```bash
  docker-compose logs streamlit
  docker-compose logs fhir-server
  ```

### Debug Mode
Enable debug mode in `.env`:
```bash
DEBUG=true
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is not licensed yet, since it's a personal project and under development.

## Support

For support:
1. Check the troubleshooting section
2. Open an issue in the GitHub repository
3. Contact the maintainers

## Acknowledgments

- HAPI FHIR for the FHIR server implementation
- Streamlit community for the web framework
- Contributors and testers
