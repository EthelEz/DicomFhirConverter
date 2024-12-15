import matplotlib.pyplot as plt
import pydicom
import os
import importlib.util
import sys
def gender(gender):
    if gender == "M":
        return "male"
    elif gender == "F":
        return "female"
    else:
        return "unknown"
    
def study_date(study_date):
    if study_date:
        return study_date[:4] + "-" + study_date[4:6] + "-" + study_date[6:]
    else:
        return "unknown"
    

def extract_age(age_code):

    if not age_code or len(age_code) < 2:
        return {"error": "Invalid age code"}
    
    # Extract the numeric part and the unit
    age = int(age_code[:-1])  # All but the last character
    unit = age_code[-1].upper()  # Last character

    # Map the unit to a human-readable format
    unit_mapping = {
        "Y": "years",
        "M": "months",
        "D": "days",
        "W": "weeks"
    }

    return {
        "age": age,
        "unit": unit_mapping.get(unit, "unknown")
    }

# age_code = "071Y"
# age_info = extract_age(age_code)

# print(f"Extracted Age: {age_info['age']} {age_info['unit']}")

import base64
from io import BytesIO
from PIL import Image

def convert_dicom_to_image(dicom_file, format="TIFF"):
    pixel_array = dicom_file.pixel_array
    image = Image.fromarray(pixel_array)
    buffer = BytesIO()
    image.save(buffer, format=format)
    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_string

# Add the dicomConverter directory to Python path
converter_path = "/Users/ethelschinedu/corhorApp/dicomConverter"
sys.path.append(converter_path)

# Import the main and query modules
def import_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

main_module = import_module("main", os.path.join(converter_path, "main.py"))
query_module = import_module("query", os.path.join(converter_path, "query.py"))

def get_fhir_data():
    """Fetch FHIR data without saving to CSV"""
    import asyncio
    
    async def fetch_data():
        client = query_module.SyncFHIRClient(
            url=query_module.FHIR_URL,
            extra_headers={"Content-Type": "application/fhir+json"}
        )
        
        all_records = []
        reports = client.resources('DiagnosticReport').fetch_all()
        
        for report in reports:
            if report['status'] == 'final' and report['code']['coding'][0]['code'] == '36642-7':
                record = {
                    'recorded_date': report.get('effectiveDateTime'),
                    'image_title': report.get_by_path('presentedForm.0.title'),
                    'sopinstanceUID': report.get('id'),
                    'image_data': report.get_by_path('presentedForm.0.data'),  # Add image data
                    'patient_id': None,
                    'gender': None,
                    'age': None
                }
                
                # Add patient data
                patient_data = report.get_by_path('subject.reference')
                if patient_data and '/' in patient_data:
                    patient_id = patient_data.split('/')[1]
                    record['patient_id'] = patient_id
                    patients = client.resources('Patient').search(_id=patient_id).fetch_all()
                    for patient in patients:
                        record['gender'] = patient.get('gender')
                        record['age'] = patient.get_by_path("extension.0.valueString")
                
                for observation in report.get('result', []):
                    reference = observation.get('reference')
                    if reference:
                        obs_id = reference.split('/')[1]
                        body_paths = client.resources('Observation').search(_id=obs_id).fetch_all()
                        for body_path in body_paths:
                            code = body_path.get_by_path('code.coding.0.code')
                            if code == '65737-9':
                                # Add study-related fields
                                record.update({
                                    'studyinstanceuid': body_path.get('id'),
                                    'study_id': body_path.get_by_path('identifier.0.value'),
                                    'body_part_examined': body_path.get_by_path('component.0.valueString'),
                                    'scan_options': body_path.get_by_path('component.1.valueString'),
                                    'scan_mode': body_path.get_by_path('component.2.valueString'),
                                    'kvp': body_path.get_by_path('component.3.valueString'),
                                    'collection_diameter': body_path.get_by_path('component.4.valueString'),
                                    'protocol_name': body_path.get_by_path('component.5.valueString'),
                                    'reconstruction_diameter': body_path.get_by_path('component.6.valueString'),
                                    'gantry_detector_tilt': body_path.get_by_path('component.7.valueString'),
                                    'table_height': body_path.get_by_path('component.8.valueString'),
                                    'rotation_direction': body_path.get_by_path('component.9.valueString'),
                                    'exposure_time': body_path.get_by_path('component.10.valueString'),
                                    'xray_tube_current': body_path.get_by_path('component.11.valueString'),
                                    'exposure': body_path.get_by_path('component.12.valueString'),
                                    'filter_type': body_path.get_by_path('component.13.valueString'),
                                    'generator_power': body_path.get_by_path('component.14.valueString'),
                                    'focal_spots': body_path.get_by_path('component.15.valueString'),
                                    'convolution_kernel': body_path.get_by_path('component.16.valueString'),
                                    'patient_position': body_path.get_by_path('component.17.valueString'),
                                    'spiral_pitch_factor': body_path.get_by_path('component.18.valueString'),
                                    'ctdi_vol': body_path.get_by_path('component.19.valueString')
                                })

                                # Add imaging study data
                                imaging_data = body_path.get_by_path('derivedFrom.0.reference')
                                if imaging_data is not None and '/' in patient_data:
                                    image_id = imaging_data.split('/')[1]
                                    images = client.resources('ImagingStudy').search(_id=image_id).fetch_all()
                                    for image in images:
                                        record.update({
                                            'accession_number': image.get_by_path('series.0.number'),
                                            'modality': image.get_by_path('series.0.modality.code'),
                                            'study_description': image.get_by_path('series.0.description')
                                        })

                                        # Add device data
                                        device_data = image.get_by_path('subject.reference')
                                        if device_data is not None and '/' in device_data:
                                            device_id = device_data.split('/')[1]
                                            devices = client.resources('Device').search(_id=device_id).fetch_all()
                                            for device in devices:
                                                record.update({
                                                    'manufacturer': device.get('manufacturer'),
                                                    'model_number': device.get('modelNumber')
                                                })

                            if code == '65737-8':
                                # Add series-related fields
                                record.update({
                                    'seriesinstanceuid': body_path.get('id'),
                                    'seriesnumber': body_path.get_by_path('component.0.valueString'),
                                    'acquisitionnumber': body_path.get_by_path('component.1.valueString'),
                                    'instancenumber': body_path.get_by_path('component.2.valueString'),
                                    'patientorientation': body_path.get_by_path('component.3.valueString'),
                                    'imagepositionpatient': body_path.get_by_path('component.4.valueString'),
                                    'imageorientationpatient': body_path.get_by_path('component.5.valueString'),
                                    'frameofreferenceuid': body_path.get_by_path('component.6.valueString'),
                                    'positionreferenceindicator': body_path.get_by_path('component.7.valueString'),
                                    'slicelocation': body_path.get_by_path('component.8.valueString'),
                                    'samplesperpixel': body_path.get_by_path('component.9.valueString'),
                                    'photometricinterpretation': body_path.get_by_path('component.10.valueString'),
                                    'rows': body_path.get_by_path('component.11.valueString'),
                                    'columns': body_path.get_by_path('component.12.valueString'),
                                    'pixelspacing': body_path.get_by_path('component.13.valueString'),
                                    'bitsallocated': body_path.get_by_path('component.14.valueString'),
                                    'bitsstored': body_path.get_by_path('component.15.valueString'),
                                    'highbit': body_path.get_by_path('component.16.valueString'),
                                    'pixelrepresentation': body_path.get_by_path('component.17.valueString'),
                                    'windowcenter': body_path.get_by_path('component.18.valueString'),
                                    'windowwidth': body_path.get_by_path('component.19.valueString'),
                                    'rescaleintercept': body_path.get_by_path('component.20.valueString'),
                                    'rescalevalue': body_path.get_by_path('component.21.valueString'),
                                    'performedproceduresstepid': body_path.get_by_path('component.22.valueString'),
                                    # 'pixeldata': body_path.get_by_path('component.23.valueString')
                                })
                
                all_records.append(record)
        
        return all_records
    
    return asyncio.run(fetch_data())