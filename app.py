import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import importlib.util
import base64
from io import BytesIO
import numpy as np
from PIL import Image
import pydicom
import shutil 
from pydicom.pixel_data_handlers.util import apply_voi_lut
import matplotlib.pyplot as plt
from process import get_fhir_data, convert_dicom_to_image, converter_path, main_module


async def convert_to_fhir(uploaded_files):
    """Convert uploaded DICOM files to FHIR"""
    temp_dir = Path(converter_path) / "temp"
    st.write(f"Processing {len(uploaded_files)} files")
    st.write(f"Converter path: {converter_path}")
    
    # Clean and create temp directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)
    
    saved_files = []
    
    for uploaded_file in uploaded_files:
        # Debug the file content
        st.write(f"File details - Name: {uploaded_file.name}, Size: {uploaded_file.size} bytes")
        try:
            # Verify it's a valid DICOM file
            dicom_data = pydicom.dcmread(uploaded_file)
            st.write(f"Valid DICOM file detected: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Invalid DICOM file {uploaded_file.name}: {str(e)}")
            continue
        
        file_name = uploaded_file.name
        if not file_name.lower().endswith('.dcm'):
            file_name = f"{file_name}.dcm"
        
        file_path = temp_dir / file_name
        st.write(f"Saving to: {file_path}")
        
        with open(file_path, "wb") as f:
            file_content = uploaded_file.getvalue()
            f.write(file_content)
            st.write(f"Saved {len(file_content)} bytes")
        
        saved_files.append(file_name)
    
    # Verify files in temp directory
    actual_files = list(temp_dir.glob("*"))
    st.write("Files in temp directory:")
    for file in actual_files:
        st.write(f"- {file.name} ({file.stat().st_size} bytes)")
        # Verify file is readable as DICOM
        try:
            dicom_data = pydicom.dcmread(file)
            st.write(f"  ✓ Successfully verified as DICOM")
        except Exception as e:
            st.write(f"  ✗ Failed DICOM verification: {str(e)}")
    
    try:
        st.write("Starting conversion...")
        # st.write(f"Calling main_module.main with path: {str(temp_dir)}")
        processed_files = await main_module.main(str(temp_dir))
        
        if processed_files:
            st.success(f"Successfully converted {len(processed_files)} DICOM files to FHIR!")
            for file in processed_files:
                st.write(f"Processed: {file}")
        else:
            st.warning("No DICOM files were processed.")
            # st.write("Troubleshooting information:")
            # st.write(f"- Temp directory: {temp_dir}")
            # st.write(f"- Files saved: {saved_files}")
            # st.write(f"- Files found: {actual_files}")
    except Exception as e:
        st.error(f"Error during conversion: {str(e)}")
        st.write(f"Error type: {type(e).__name__}")
        import traceback
        st.write("Traceback:", traceback.format_exc())
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def convert_dicom_to_image(image_data, output_format="WEBP"):
    try:
        # Decode base64 string to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Open the image directly with PIL
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to output format
        buffer = BytesIO()
        image.save(buffer, format=output_format)
        image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return image_string, image
    except Exception as e:
        print(f"Error converting image: {str(e)}")
        return None, None


def main():
    st.title("DICOM to FHIR Converter")
    st.subheader("Ensure FHIR Server is up and running before continuing")
    # File upload section
    # st.subheader("Upload DICOM Files")
    uploaded_files = st.file_uploader("Choose DICOM files", 
                                    type=['dcm'], 
                                    accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Convert to FHIR"):
            # Add spinner while converting
            with st.spinner('Converting DICOM files to FHIR...'):
                # Use asyncio to run the async function
                import asyncio
                asyncio.run(convert_to_fhir(uploaded_files))
    
    # Display data section
    st.subheader("FHIR Data Preview")
    if st.button("Show Data"):
        with st.spinner("Fetching data..."):
            records = get_fhir_data()
            if records:
                df = pd.DataFrame(records)
                
                # Store the DataFrame in the session state
                st.session_state['df'] = df
                st.session_state['show_data'] = True  # Add flag to maintain state

                # Display the DataFrame without the image data column
                display_df = df.drop(columns=['image_data'])
                # st.dataframe(display_df, use_container_width=True)

                # Show the total number of records
                st.write(f"Total records: {len(display_df)}")

                # Create a scrollable container with fixed height
                with st.container():
                    st.write("Showing first 5 rows (scroll to see more):")
                    st.dataframe(
                        display_df,
                        height=200,  # Fixed height in pixels
                        use_container_width=True
                    )

    # Move image viewer outside the if statement
    if 'df' in st.session_state:
        st.header("Image Viewer")
        df = st.session_state['df']
        
        # Create two columns - one for the selector and one for the download button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_row = st.selectbox(
                "Select a row to view the image", 
                range(len(df)),
                format_func=lambda x: f"Record {x+1} - {df.iloc[x]['recorded_date']}"
            )

        if selected_row is not None:
            image_data = df.iloc[selected_row]['image_data']
            if image_data:
                try:
                    st.write(f"Processed image for record {selected_row + 1}")
                    image_string, pil_image = convert_dicom_to_image(image_data)
                    if image_string:
                        st.image(BytesIO(base64.b64decode(image_string)), caption=f"DICOM Image - Record {selected_row + 1}")
                        
                        # Add download button in the second column
                        with col2:
                            # Convert PIL image to bytes
                            img_byte_arr = BytesIO()
                            pil_image.save(img_byte_arr, format='WEBP')
                            img_byte_arr = img_byte_arr.getvalue()
                            
                            st.download_button(
                                label="⬇️ Download Image",
                                data=img_byte_arr,
                                file_name=f"dicom_image_{selected_row + 1}.webp",
                                mime="image/webp",
                            )
                    else:
                        st.error("Failed to convert image data")
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
                    st.write("Error details:", str(e))
            else:
                st.info("No image data available for this record")

    # Download CSV section
    if st.button("Download as CSV"):
        with st.spinner("Preparing CSV..."):
            records = get_fhir_data()
            if records:
                df = pd.DataFrame(records)
                df_for_csv = df.drop(columns=['image_data'])
                csv = df_for_csv.to_csv(index=False)
                st.download_button(
                    label="Click to Download",
                    data=csv,
                    file_name="fhir_data.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data available for download.")

if __name__ == "__main__":
    main()