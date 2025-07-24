import subprocess
from dirpicker import DirectoryPicker  # Assuming DirectoryPicker is defined in directory_picker.py
import sys
import os  # ### ZMIANA ###: Import modułu os do operacji na systemie plików

# This is the main execution block that uses the DirectoryPicker class.
# It gathers the necessary inputs and then constructs and runs the command-line tool.
if __name__ == "__main__":
    # The DirectoryPicker class definition from the previous context is assumed to be present here.
    picker = DirectoryPicker()

    print("--- Configuring IMOPSE Execution ---")
    print("Please provide the necessary paths and parameters.")
    print("You can use aliases (e.g., 'save my_dir', 'goto my_dir') in the pickers.")
    print("For optional values, you can cancel the input prompt (Ctrl+C) to skip them.")

    # --- Gather all required and optional parameters ---
    exefile_path = picker.get_file(
        "imopse_exe",
        prompt_message="Select the imopse.exe executable file"
    )
    method_config_path = picker.get_file(
        "method_config",
        prompt_message="Select the Method Config file"
    )
    problem_name = picker.get_value(
        "problem_name",
        prompt_message="Enter the Problem Name (e.g., 'TSP')"
    )
    problem_instance_path = picker.get_file(
        "problem_instance",
        prompt_message="Select the Problem Instance file"
    )
    # Użytkownik wybiera *bazowy* katalog wyjściowy
    base_output_directory = picker.get_directory(
        "output_dir",
        prompt_message="Select the BASE Output Directory (e.g., C:/results)"
    )
    # Optional parameters: get_value returns None if user cancels (Ctrl+C)
    executions_count = picker.get_value(
        "exec_count",
        prompt_message="Enter Executions Count (optional, cancel to skip)",
        value_type=int,
        force_ask=False
    )
    seed = picker.get_value(
        "seed",
        prompt_message="Enter Seed (optional, cancel to skip)",
        value_type=int,
        force_ask=False
    )

    # --- Validate required inputs before proceeding ---
    required_params = {
        "Executable File": exefile_path,
        "Method Config Path": method_config_path,
        "Problem Name": problem_name,
        "Problem Instance Path": problem_instance_path,
        "Base Output Directory": base_output_directory
    }

    if any(value is None for value in required_params.values()):
        print("\n--- Execution Aborted ---")
        for name, value in required_params.items():
            if value is None:
                print(f"Missing required input: {name}")
        sys.exit(1)

    ### ZMIANA START ###
    # --- Określenie i utworzenie katalogu wyjściowego specyficznego dla danego uruchomienia (r1, r2, ...) ---
    try:
        # Znajdź najwyższy istniejący numer uruchomienia w katalogu bazowym
        max_run_num = 0
        # Przeskanuj elementy w bazowym katalogu wyjściowym
        for item in os.listdir(base_output_directory):
            # Zbuduj pełną ścieżkę do elementu, aby sprawdzić, czy jest to katalog
            item_path = os.path.join(base_output_directory, item)
            # Sprawdź, czy: 1) to katalog, 2) nazwa zaczyna się na 'r', 3) reszta nazwy to cyfry
            if os.path.isdir(item_path) and item.startswith('r') and item[1:].isdigit():
                run_num = int(item[1:])
                if run_num > max_run_num:
                    max_run_num = run_num

        # Numer nowego uruchomienia to kolejny numer w sekwencji
        next_run_num = max_run_num + 1
        # Utwórz pełną ścieżkę do nowego katalogu (np. C:/results/r1)
        run_specific_output_dir = os.path.join(base_output_directory, f"r{next_run_num}")

        # Utwórz katalog, jeśli nie istnieje
        print(f"\nCreating run-specific output directory: {run_specific_output_dir}")
        os.makedirs(run_specific_output_dir, exist_ok=True)

    except FileNotFoundError:
        print(f"Error: The selected base output directory does not exist: {base_output_directory}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while creating the run-specific directory: {e}")
        sys.exit(1)
    ### ZMIANA KONIEC ###

    # --- Construct the command as a list for subprocess ---
    command = [
        exefile_path,
        method_config_path,
        problem_name,
        problem_instance_path,
        run_specific_output_dir  # ### ZMIANA ###: Użyj nowej, specyficznej ścieżki
    ]

    # Append optional arguments if they were provided
    if executions_count is not None:
        command.append(str(executions_count))
    if seed is not None:
        command.append(str(seed))

    # --- Execute the command ---
    print("\n" + "="*50)
    print("--- Executing Command ---")
    # Use subprocess.list2cmdline to create a printable string version of the command
    # This is helpful for debugging and ensures correct quoting for paths with spaces.
    printable_command = subprocess.list2cmdline(command)
    print(f"Running: {printable_command}")
    print("="*50 + "\n")

    try:
        # Using subprocess.run to execute the command
        # capture_output=True saves stdout and stderr to the result object
        # text=True decodes them as text
        # check=True will raise a CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("--- STDOUT ---")
        print(result.stdout)
        if result.stderr:
            print("--- STDERR ---")
            print(result.stderr)
        print("\n--- Execution Finished Successfully ---")

    except FileNotFoundError:
        print(f"Error: The executable was not found at the specified path: '{exefile_path}'")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # This block runs if the executable returns an error (non-zero exit code)
        print(f"--- Execution Failed (Exit Code: {e.returncode}) ---")
        print("\n--- STDOUT ---")
        print(e.stdout)
        print("\n--- STDERR ---")
        print(e.stderr)
        sys.exit(e.returncode)
    except Exception as e:
        # Catch any other unexpected errors during execution
        print(f"An unexpected error occurred while running the subprocess: {e}")
        sys.exit(1)