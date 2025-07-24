import os

def gather_cpp_headers(root_folder, output_file):
    """
    Recursively gathers C++ header files from a folder and its subdirectories
    and combines them into a single text file.

    Args:
        root_folder (str): The path to the root folder to search.
        output_file (str): The path to the output text file.
    """
    header_extensions = ('.h', '.hpp', '.hh')
    #header_extensions = ('.cpp')
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for dirpath, _, filenames in os.walk(root_folder):
                for filename in filenames:
                    if filename.endswith(header_extensions):
                        file_path = os.path.join(dirpath, filename)
                        outfile.write(f"{file_path}\n")
                        outfile.write("=============\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                outfile.write(infile.read())
                                outfile.write("\n\n")
                        except Exception as e:
                            outfile.write(f"[Error reading file: {e}]\n\n")
        print(f"Successfully gathered all header files into '{output_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Get user input for the folder to search and the output file name
    start_directory = input("Enter the path to the directory to search: ")
    output_filename = input("Enter the name of the output file (e.g., all_headers.txt): ")

    # Validate the directory path
    if not os.path.isdir(start_directory):
        print("Error: The specified directory does not exist.")
    else:
        gather_cpp_headers(start_directory, output_filename)