id: transform-dicom-to-fhir
canonical: http://localhost:8090/fhir/ig/transform-dicom-to-fhir
url: http://localhost:8090/fhir/ig/transform-dicom-to-fhir/index.html
version: 1.0.0
name: TransformDICOMToFHIR
status: active
title: Transform DICOM to FHIR
publisher: Example Organization
fhirVersion: 4.0.1
template: hl7.fhir.template
contact:
  - name: Support Team
    email: nedu47@gmail.com

Profiles:

Profile: NHS_Patient
Parent: Patient
Title: "NHS Digital Patient Profile"
Description: "A Patient profile following NHS Digital standards."
* id MS
* active MS
* extension[http://hl7.org/fhir/StructureDefinition/patient-age] MS
* gender MS

Profile: NHS_Device
Parent: Device
Title: "NHS Digital Device Profile"
Description: "A Device profile for representing DICOM devices."
* identifier MS
* manufacturer MS
* modelNumber MS
* status MS

Profile: NHS_ImagingStudy
Parent: ImagingStudy
Title: "NHS Digital Imaging Study Profile"
Description: "An ImagingStudy profile for DICOM studies."
* series[0].uid MS
* series[0].modality MS
* series[0].description MS
* subject.reference MS
* status MS

Profile: NHS_Observation
Parent: Observation
Title: "NHS Digital Observation Profile"
Description: "An Observation profile for DICOM metadata."
* code MS
* status MS
* component[0].code MS

Profile: NHS_DiagnosticReport
Parent: DiagnosticReport
Title: "NHS Digital Diagnostic Report Profile"
Description: "A DiagnosticReport profile representing DICOM data."
* code MS
* status MS
* result MS
* presentedForm.contentType MS

Extensions:

Extension: PatientAge
Id: patient-age
Title: "Patient Age"
Description: "Extension for patient age derived from DICOM."
* valueString MS

ValueSets:

ValueSet: ModalitySystem
Id: modality-system
Title: "Modality System"
Description: "A value set for DICOM modality codes."
* #CT "Computed Tomography"
* #MR "Magnetic Resonance"
* #XR "X-Ray"

Instances:

Instance: ExamplePatient
InstanceOf: NHS_Patient
Title: "Example Patient"
Description: "An example Patient instance."
* id = "example-patient"
* active = false
* gender = #male
* extension[patient-age].valueString = "45"

Instance: ExampleDevice
InstanceOf: NHS_Device
Title: "Example Device"
Description: "An example Device instance."
* id = "example-device"
* identifier[0].value = "1.2.840.10008.1.2"
* manufacturer = "Example Manufacturer"
* modelNumber = "Model123"
* status = #active

Instance: ExampleImagingStudy
InstanceOf: NHS_ImagingStudy
Title: "Example Imaging Study"
Description: "An example ImagingStudy instance."
* id = "example-imaging-study"
* subject.reference = "Device/example-device"
* status = #registered
* series[0].uid = "1.2.840.10008.1.3"
* series[0].modality.code = #CT
* series[0].description = "CT Chest"

Instance: ExampleObservation
InstanceOf: NHS_Observation
Title: "Example Observation"
Description: "An example Observation instance."
* id = "example-observation"
* code.coding[0].code = "65737-9"
* code.coding[0].system = "http://loinc.org"
* code.coding[0].display = "Body part examined"
* status = #registered

Instance: ExampleDiagnosticReport
InstanceOf: NHS_DiagnosticReport
Title: "Example Diagnostic Report"
Description: "An example DiagnosticReport instance."
* id = "example-diagnostic-report"
* code.coding[0].code = "36642-7"
* code.coding[0].system = "http://loinc.org"
* code.coding[0].display = "Chest X-ray"
* status = #registered
* result[0].reference = "Observation/example-observation"
* presentedForm[0].contentType = "image/png"
* presentedForm[0].data = "<base64-encoded-image>"