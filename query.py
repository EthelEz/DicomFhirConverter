from fhirpy import SyncFHIRClient
import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd  # Add pandas import

# Set up the Azure authentication
_ = load_dotenv(find_dotenv())

FHIR_URL = os.environ["local_url"]

async def main():

    # Set up the FHIR client
    client = SyncFHIRClient(
        url=FHIR_URL, 
        # authorization=f"Bearer {access_token}",
        extra_headers={"Content-Type": "application/fhir+json"})
    
    # Create a list to store all records
    all_records = []
    
    reports = client.resources('DiagnosticReport').fetch_all() 
    for report in reports:
        if report['status'] == 'final' and report['code']['coding'][0]['code'] == '36642-7':
            # Initialize a dictionary for each record
            record = {
                'recorded_date': report.get('effectiveDateTime'),
                'sopinstanceUID': report.get('id'),
                'image_data': report.get_by_path('presentedForm.0.data'),
                'image_title': report.get_by_path('presentedForm.0.title'),
                'patient_id': None,
                'gender': None,
                'age': None
            }

            patient_data = report.get_by_path('subject.reference')
            if patient_data is not None and '/' in patient_data:
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
                                'ctdi_vol': body_path.get_by_path('component.19.valueString'),
                            })
                            imaging_data = body_path.get_by_path('derivedFrom.0.reference')
                            if imaging_data is not None and '/' in patient_data:
                                image_id = imaging_data.split('/')[1]
                                images = client.resources('ImagingStudy').search(_id=image_id).fetch_all()
                                for image in images:
                                    record.update({
                                        'accession_number': image.get_by_path('series.0.number'),
                                        'modality': image.get_by_path('series.0.modality.code'),
                                        'study_description': image.get_by_path('series.0.description'),
                                    })
                                    device_data = image.get_by_path('subject.reference')
                                    # print(device_data)
                                    if device_data is not None and '/' in device_data:
                                        device_id = device_data.split('/')[1]
                                        devices = client.resources('Device').search(_id=device_id).fetch_all()
                                        # print(devices)
                                        for device in devices:
                                            record.update({
                                                'manufacturer': device.get('manufacturer'),
                                                'model_number': device.get('modelNumber'),
                                            })
                            
                        if code == '65737-8':
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
                                # 'pixeldata': body_path.get_by_path('component.23.valueString'),
                            })
            
            # Add the complete record to our list
            all_records.append(record)

    # Create DataFrame and save to CSV
    df = pd.DataFrame(all_records)
    df.to_csv('dicom_dataset.csv', index=False)
    print(f"Data saved to dicom_data.csv with {len(all_records)} records")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())