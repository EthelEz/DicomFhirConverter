To profile and generate the FHIR Implementation Guide (IG) for this project from this SUSHI file, follow these steps:

1. Install Prerequisites:
    - Install Node.js (v14 or later recommended)
    - Install SUSHI globally:
    ```bash
    npm install -g fsh-sushi
    ```
    - Install Jekyll (required by IG Publisher):
    ```bash
    gem install jekyll
    ```
    - Install Ruby and Ruby Gems (required for Jekyll)
    ```bash
    # For Ubuntu/Debian
    sudo apt-get install ruby-full build-essential
    # For macOS (using Homebrew)
    brew install ruby
    ```

2. Clone and Navigate:
    ```bash
    git clone https://github.com/nedu47/dicomConverter.git
    cd dicomConverter/dicom2fhir
    ```

3. Set up SUSHI Project:
    - Create a `sushi-config.yaml` file in the project root if not present:
    ```yaml
    id: dicom-fhir-converter
    canonical: http://localhost:8090/fhir/ig/transform-dicom-to-fhir
    name: DICOMtoFHIRImplementationGuide
    status: draft
    version: 0.1.0
    fhirVersion: 4.0.1
    FSHOnly: false
    applyExtensionMetadataToRoot: false
    dependencies:
      hl7.fhir.r4.core: 4.0.1
    ```

4. Verify FSH Files:
    - Ensure your `ig.fsh` file is in the correct location:
    ```bash
    ls input/fsh/ig.fsh
    ```
    - Validate FSH syntax:
    ```bash
    sushi -s input/fsh/ig.fsh
    ```

5. Run SUSHI:
    ```bash
    sushi .
    ```

6. Set up IG Publisher:
    - Create a `_genonce.sh` (Unix) or `_genonce.bat` (Windows) script:
    ```bash
    #!/bin/bash
    publisher_jar=publisher.jar
    input_cache_path=./input-cache/
    
    if test -f "$publisher_jar"; then
        java -jar "$publisher_jar" -ig . $*
    else
        if test -f "$input_cache_path$publisher_jar"; then
            java -jar "$input_cache_path$publisher_jar" -ig . $*
        else
            wget https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar -O "$publisher_jar"
            java -jar "$publisher_jar" -ig . $*
        fi
    fi
    ```

7. Create Directory Structure:
    ```bash
    mkdir -p input/images
    mkdir -p input/includes
    mkdir -p input/resources
    mkdir -p input/pagecontent
    ```

8. Run IG Publisher:
    ```bash
    ./_genonce.sh  # For Unix
    # OR
    _genonce.bat   # For Windows
    ```

9. View and Validate:
    - Open `output/index.html` in a web browser
    - Check `output/qa.html` for validation results
    - Review generated profiles in `output/profiles`

10. Troubleshooting:
    - Check logs in `fsh-generated/logs`
    - Verify FHIR version compatibility
    - Common issues:
        - Java version: Ensure Java 8 or later is installed
        - Memory issues: Add `-Xmx2G` to Java commands if needed
        - Path issues: Ensure all paths are correct for your OS

Note: 
- Keep your SUSHI and IG Publisher versions updated
- The IG Publisher may take several minutes to run
- Ensure you have at least 4GB of free memory for the IG Publisher
- Consider using `_updatePublisher.sh` script to manage publisher updates
