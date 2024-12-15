from fhirpy import SyncFHIRClient
import os
import pydicom
import base64
from dotenv import load_dotenv, find_dotenv
from process import gender, extract_age, study_date, convert_dicom_to_image

# Set up the Azure authentication
_ = load_dotenv(find_dotenv())

FHIR_URL = os.environ["local_url"]

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main(directory_path=None):
    logger.info(f"Starting DICOM to FHIR conversion from directory: {directory_path}")

# async def main():

    # Set up the FHIR client
    client = SyncFHIRClient(
        url=FHIR_URL, 
        # authorization=f"Bearer {access_token}",
        extra_headers={"Content-Type": "application/fhir+json"})
    
    # Use the provided directory_path instead of the script's directory
    search_path = directory_path if directory_path else os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Searching for DICOM files in: {search_path}")
    
    processed_files = []  # Add this to track processed files
    
    for dicom_file in os.listdir(search_path):
        if dicom_file.endswith(".dcm"):
            full_path = os.path.join(search_path, dicom_file)
            logger.info(f"Processing file: {dicom_file}")
            try:
                ds = pydicom.dcmread(full_path)

                age_info = extract_age(ds.PatientAge)

                # Convert MultiValue attributes to lists or strings
                def convert_to_serializable(value):
                    if isinstance(value, pydicom.multival.MultiValue):
                        return list(value)  # Convert to list
                    return value
        
                # Create or update a Patient resource
                patient_data = client.resource(
                    'Patient',
                    id=ds.PatientID,
                    active=False,
                    # birthDate="1980-01-01",
                    gender=gender(ds.PatientSex),
                    extension=[{
                        "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                        "valueString": age_info["age"]
                    }],
                    # name=[{"family": "Smith", "given": ["John"]}]
                )
                patient_data.save()
                print(patient_data.id)
                
                if patient_data['active'] is False:
                    patient_data.active = True
                patient_data.save()

                # Create or update a device resource 
                device_data = client.resource(
                    'Device',
                    id=ds.SOPInstanceUID,
                    status="active",
                    identifier=[{"value":ds.SOPClassUID}],
                    manufacturer=ds.Manufacturer,
                    modelNumber=ds.ManufacturerModelName
                )
                device_data.save()

                if device_data['status'] == "active":
                    device_data.status = "inactive"
                device_data.save()

                # Create or update an ImagingStudy resource
                imaging_study_data = client.resource(
                    'ImagingStudy',
                    id=ds.StudyInstanceUID,
                    subject={"reference": "Device"+"/"+device_data['id']},
                    status="registered",
                    # performer= [{"actor": {"reference": "Device"+"/"+device_data['id']}}],
                    started=study_date(ds.StudyDate),
                    # numberOfInstances=convert_to_serializable(ds.SeriesDescription),
                    series=[
                        {
                            "uid": ds.SOPInstanceUID,
                            "number": ds.AccessionNumber,
                            "modality": {
                                "system": "http://dicom.nema.org/resources/ontology/DCM",
                                "code": ds.Modality
                                },
                            "description": convert_to_serializable(ds.StudyDescription),
                            "bodySite": convert_to_serializable(ds.BodyPartExamined),
                        }
                    ]
                )
                imaging_study_data.save()

                if imaging_study_data['status'] == "registered":
                    imaging_study_data.status = "available"
                imaging_study_data.save()

                # Create or update an Observation resource
                body_part_data = client.resource(
                    'Observation',
                    id=ds.StudyInstanceUID,
                    status="registered",
                    code={"coding": [{"system": "http://loinc.org", "code": "65737-9", "display": "Body part examined"}]},
                    identifier=[{"value":ds.StudyID}],
                    subject={"reference": "Patient"+"/"+patient_data['id']},
                    derivedFrom=[{"reference": "ImagingStudy"+"/"+imaging_study_data['id']}],
                    component=[
                        {"code":{"coding":[{"system":"http://loinc.org","code":"bodypartexamined"}]},"valueString": convert_to_serializable(ds.BodyPartExamined)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"scanoptions"}]},"valueString": convert_to_serializable(ds.ScanOptions)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"scanmode"}]},"valueString": convert_to_serializable(ds.SliceThickness)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"kvp"}]},"valueString": convert_to_serializable(ds.KVP)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"collectiondiameter"}]},"valueString": convert_to_serializable(ds.DataCollectionDiameter)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"protocolname"}]},"valueString": convert_to_serializable(ds.ProtocolName)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"reconstructiondiameter"}]},"valueString": convert_to_serializable(ds.ReconstructionDiameter)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"gantrydetectortilt"}]},"valueString": convert_to_serializable(ds.GantryDetectorTilt)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"tableheight"}]},"valueString": convert_to_serializable(ds.TableHeight)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"rotationdirection"}]},"valueString": convert_to_serializable(ds.RotationDirection)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"exposuretime"}]},"valueString": convert_to_serializable(ds.ExposureTime)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"xraytubecurrent"}]},"valueString": convert_to_serializable(ds.XRayTubeCurrent)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"exposure"}]},"valueString": convert_to_serializable(ds.Exposure)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"filtertype"}]},"valueString": convert_to_serializable(ds.FilterType)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"generatorpower"}]},"valueString": convert_to_serializable(ds.GeneratorPower)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"focalspot"}]},"valueString": convert_to_serializable(ds.FocalSpots)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"convolutionkernel"}]},"valueString": convert_to_serializable(ds.ConvolutionKernel)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"patientposition"}]},"valueString": convert_to_serializable(ds.PatientPosition)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"spiralpitchfactor"}]},"valueString": convert_to_serializable(ds.SpiralPitchFactor)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"ctdivol"}]},"valueString": convert_to_serializable(ds.CTDIvol)}
                    ]
                )
                body_part_data.save()
                
                if body_part_data['status'] == "registered":
                    body_part_data.status = "final"
                body_part_data.save()

                # Create or update an Observation resource
                image_part_data = client.resource(
                    'Observation',
                    id=ds.SeriesInstanceUID,
                    status="registered",
                    code={"coding": [{"system": "http://loinc.org", "code": "65737-8", "display": "Body part examined"}]},
                    identifier=[{"value":ds.StudyID}],
                    subject={"reference": "Patient"+"/"+patient_data['id']},
                    derivedFrom=[{"reference": "Observation"+"/"+body_part_data['id']}],
                    component=[
                        {"code":{"coding":[{"system":"http://loinc.org","code":"seriesnumber"}]},"valueString": convert_to_serializable(ds.SeriesNumber)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"acquisitionnumber"}]},"valueString": convert_to_serializable(ds.AcquisitionNumber)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"instancenumber"}]},"valueString": convert_to_serializable(ds.InstanceNumber)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"patientorientation"}]},"valueString": convert_to_serializable(ds.PatientOrientation)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"imagepositionpatient"}]},"valueString": convert_to_serializable(ds.ImagePositionPatient)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"imageorientationpatient"}]},"valueString": convert_to_serializable(ds.ImageOrientationPatient)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"frameofreferenceuid"}]},"valueString": convert_to_serializable(ds.FrameOfReferenceUID)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"positionreferenceindicator"}]},"valueString": convert_to_serializable(ds.PositionReferenceIndicator)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"slicelocation"}]},"valueString": convert_to_serializable(ds.SliceLocation)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"samplesperpixel"}]},"valueString": convert_to_serializable(ds.SamplesPerPixel)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"photometricinterpretation"}]},"valueString": convert_to_serializable(ds.PhotometricInterpretation)},    
                        {"code":{"coding":[{"system":"http://loinc.org","code":"rows"}]},"valueString": convert_to_serializable(ds.Rows)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"columns"}]},"valueString": convert_to_serializable(ds.Columns)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"pixelspacing"}]},"valueString": convert_to_serializable(ds.PixelSpacing)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"bitsallocated"}]},"valueString": convert_to_serializable(ds.BitsAllocated)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"bitsstored"}]},"valueString": convert_to_serializable(ds.BitsStored)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"highbit"}]},"valueString": convert_to_serializable(ds.HighBit)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"pixelrepresentation"}]},"valueString": convert_to_serializable(ds.PixelRepresentation)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"windowcenter"}]},"valueString": convert_to_serializable(ds.WindowCenter)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"windowwidth"}]},"valueString": convert_to_serializable(ds.WindowWidth)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"rescaleintercept"}]},"valueString": convert_to_serializable(ds.RescaleIntercept)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"rescalevalue"}]},"valueString": convert_to_serializable(ds.RescaleSlope)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"performedproceduresstepid"}]},"valueString": convert_to_serializable(ds.PerformedProcedureStepID)},
                        {"code":{"coding":[{"system":"http://loinc.org","code":"pixeldata"}]},"valueString": base64.b64encode(ds.PixelData).decode('utf-8')}
                    ]
                )
                image_part_data.save()
                
                if image_part_data['status'] == "registered":
                    image_part_data.status = "final"
                image_part_data.save()

                # Create or update a DiagnosticReport resource
                diagnostic_report_data = client.resource(
                    'DiagnosticReport',
                    id=ds.SOPInstanceUID,
                    status="registered",
                    code={"coding": [{"system": "http://loinc.org", "code": "36642-7", "display": "Chest X-ray"}]},
                    subject={"reference": "Patient"+"/"+patient_data['id']},
                    effectiveDateTime=study_date(ds.StudyDate),
                    imagingStudy=[{"reference": "ImagingStudy"+"/"+imaging_study_data['id']}],
                    # basedOn=[{"reference": "ServiceRequest"+"/"+service_request_data['id']}],
                    result=[{"reference": "Observation"+"/"+body_part_data['id']}, {"reference": "Observation"+"/"+image_part_data['id']}],
                    presentedForm=[{"contentType": "image/png", "data": convert_dicom_to_image(ds),"title": ds.SOPClassUID}]
                    )
                diagnostic_report_data.save()

                if diagnostic_report_data['status'] == 'registered':
                    diagnostic_report_data.status = "final"
                diagnostic_report_data.save()

                processed_files.append(dicom_file)  # Add this to track successful processing
            
                logger.info(f"Successfully processed {dicom_file}")
            except Exception as e:
                logger.error(f"Error processing {dicom_file}: {str(e)}")
                raise
            
    return processed_files

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())