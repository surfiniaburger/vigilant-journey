import os
import zipfile

def unzip_data(data_dir="data", output_dir="unzipped_data"):
    """
    Unzips all .zip files in the data_dir to the output_dir.

    Args:
        data_dir (str): The directory containing the .zip files.
        output_dir (str): The directory to extract the files to.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(data_dir):
        if filename.endswith(".zip"):
            zip_path = os.path.join(data_dir, filename)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Create a directory with the name of the zip file
                extract_path = os.path.join(output_dir, filename[:-4])
                if not os.path.exists(extract_path):
                    os.makedirs(extract_path)
                print(f"Extracting {filename} to {extract_path}...")
                zip_ref.extractall(extract_path)
                print(f"Extracted {filename} successfully.")

if __name__ == "__main__":
    unzip_data()
