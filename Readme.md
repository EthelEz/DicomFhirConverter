# Dicom Converter

This is a simple Streamlit app that allows you to convert DICOM files to FHIR resources.

## Description

The DICOM Converter is a web application built with Streamlit that enables users to:
- Upload and view DICOM medical imaging files
- Convert DICOM metadata to FHIR resources
- Visualize DICOM images
- Export FHIR resources in JSON format

## Requirements

- Python 3.10+
- Docker and Docker Compose

## Dependencies

- Streamlit
- Pandas
- Pydicom
- Pillow
- Matplotlib
- Numpy
- FHIRpy

## Installation

### Local Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/dicom-converter.git
    cd dicom-converter
    ```
2. Create and activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```


### Docker Setup

1. Make sure you have Docker and Docker Compose installed on your system:
- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

- run `docker-compose up` to start the FHIR server. To stop the server, run `docker-compose down`.

- run `streamlit run app.py` to start the Streamlit app. Usually, the app will be available at `http://localhost:8501`. if not, you check your browser's console for the correct URL.


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.


