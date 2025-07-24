import os
import sys
import json
import math

# Attempt to import readline for Unix-like systems or pyreadline3 for Windows
try:
    if sys.platform == 'win32':
        import pyreadline3 as readline_impl
    else:
        import readline as readline_impl
except ImportError:
    readline_impl = None

class DirectoryPicker:
    DEFAULT_CONFIG_FILENAME = ".path_picker_state.json"

    def __init__(self, initial_start_path=None, config_file_path=None):
        """
        Initializes the DirectoryPicker.

        Args:
            initial_start_path (str, optional): The default path to start browsing from
                if no specific start_path is provided to get_directory/get_file.
                Defaults to the current working directory.
            config_file_path (str, optional): Path to the JSON file for saving/loading state.
                Defaults to '.path_picker_state.json' in the user's home directory.
        """
        self.saved_paths = {}  # Stores alias: path
        self._initial_start_path_arg = initial_start_path # Store the argument
        self._current_browsing_path = None # Path being browsed in an active picker session

        if config_file_path:
            self.config_file_path = os.path.abspath(config_file_path)
        else:
            # MODIFICATION: Default config file to current working directory
            local_dir = os.path.abspath(os.getcwd())
            self.config_file_path = os.path.join(local_dir, self.DEFAULT_CONFIG_FILENAME)

        self._last_browsed_path = None # Loaded from state, updated on picker exit

        self.load_state() # Load saved paths and last browsed path

        # Determine effective initial start path after loading state
        if self._last_browsed_path and os.path.isdir(self._last_browsed_path):
            self._effective_initial_start_path = self._last_browsed_path
        elif self._initial_start_path_arg and os.path.isdir(self._initial_start_path_arg):
            self._effective_initial_start_path = os.path.abspath(self._initial_start_path_arg)
        else:
            self._effective_initial_start_path = os.path.abspath(os.getcwd())
            if self._initial_start_path_arg:
                 print(f"Warning: Provided initial_start_path '{self._initial_start_path_arg}' is invalid.")
        
        print(f"INFO: PathPicker state will be loaded from/saved to: {self.config_file_path}")
        if not self.saved_paths:
            print("INFO: No previous state found or loaded.")


    def load_state(self):
        """Loads saved paths and last browsed path from the config file."""
        if self.config_file_path and os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r') as f:
                    state = json.load(f)
                    self.saved_paths = state.get("saved_paths", {})
                    loaded_last_browsed = state.get("last_browsed_path")
                    if loaded_last_browsed and os.path.isdir(loaded_last_browsed):
                        self._last_browsed_path = loaded_last_browsed
                    print(f"INFO: State loaded from {self.config_file_path}")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {self.config_file_path}. Starting fresh.")
                self.saved_paths = {}
                self._last_browsed_path = None
            except IOError as e:
                print(f"Error: Could not read state file {self.config_file_path}: {e}. Starting fresh.")
                self.saved_paths = {}
                self._last_browsed_path = None
        else:
            self.saved_paths = {}
            self._last_browsed_path = None


    def save_state(self):
        """Saves the current saved_paths and last_browsed_path to the config file."""
        if not self.config_file_path:
            print("Warning: config_file_path not set. Cannot save state.")
            return

        state = {
            "saved_paths": self.saved_paths,
            "last_browsed_path": self._last_browsed_path # This should be the dir, not a file
        }
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            with open(self.config_file_path, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Error: Could not write state file {self.config_file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving state: {e}")


    def _print_help(self, mode='directory'):
        print("\n--- Path Picker Help ---")
        print("  <num>   : Navigate into the numbered subdirectory.")
        if mode == 'directory':
            print("  s       : Select the current directory.")
        elif mode == 'file':
            print("  f<num>  : Select the numbered file (e.g., 'f1', 'f2').")
            print("  s       : Select the current directory (containing these files).")

        print("  u or .. : Go to the parent directory.")
        print("  save <A>: Save the current browsed directory with alias <A>.")
        print("  goto <A>: Jump to the directory saved with alias <A>.")
        print("  list    : List all saved aliases and their paths.")
        print("  pwd     : Print the current browsed directory (full path).")
        print("  q       : Quit the picker without selection.")
        print("  h       : Show this help message.")
        print("--------------------------")

    def _display_list_in_columns(self, items, prefix="", suffix=""):
        """
        Helper function to display a list of items in dynamically adjusted columns.
        Ensures no column has more than MAX_ITEMS_PER_COLUMN items.
        """
        MAX_ITEMS_PER_COLUMN = 5
        COLUMN_SPACING = 4

        if not items:
            return

        total_items = len(items)

        if total_items <= MAX_ITEMS_PER_COLUMN:
            # Single-column display for few items
            for i, name in enumerate(items):
                print(f"  {prefix}{i+1}. {name}{suffix}")
            return

        # Multi-column display logic
        # First, format all item strings to find the necessary width for alignment
        formatted_items = []
        max_width = 0
        for i, name in enumerate(items):
            item_str = f"{prefix}{i+1}. {name}{suffix}"
            formatted_items.append(item_str)
            if len(item_str) > max_width:
                max_width = len(item_str)
        
        # Calculate the grid dimensions
        num_columns = math.ceil(total_items / MAX_ITEMS_PER_COLUMN)
        num_rows = math.ceil(total_items / num_columns)

        # Print items in column-major order
        for r in range(num_rows):
            line_parts = []
            for c in range(num_columns):
                # Calculate index for filling columns top-to-bottom, left-to-right
                index = r + c * num_rows
                if index < total_items:
                    padded_item = formatted_items[index].ljust(max_width + COLUMN_SPACING)
                    line_parts.append(padded_item)
            print("  " + "".join(line_parts).rstrip())


    def _display_current_location_and_files(self, current_path):
        normalized_current_path = os.path.normpath(os.path.abspath(current_path))
        print(f"\n--- Current Location: {normalized_current_path} ---")
        
        try:
            items = os.listdir(normalized_current_path)
        except PermissionError:
            print(f"  [Permission Denied to list contents of: {normalized_current_path}]")
            return [], []
        except FileNotFoundError:
            print(f"  [Directory not found: {normalized_current_path}]")
            return [], []

        # Separate and sort directories and files
        temp_dirs = []
        temp_files = []
        for item in items:
            item_path = os.path.join(normalized_current_path, item)
            if os.path.isdir(item_path):
                temp_dirs.append(item)
            elif os.path.isfile(item_path):
                temp_files.append(item)
        
        listed_dirs = sorted(temp_dirs)
        listed_files = sorted(temp_files)

        # --- Display Subdirectories ---
        print("Subdirectories:")
        if not listed_dirs:
            print("  (No subdirectories)")
        else:
            self._display_list_in_columns(listed_dirs, suffix=os.sep)

        # --- Display Files ---
        print("\nFiles:")
        if not listed_files:
            print("  (No files)")
        else:
            self._display_list_in_columns(listed_files, prefix="f")
            
        return listed_dirs, listed_files

    def get_value(self, alias, prompt_message=None, value_type=str, force_ask=False):
        """
        Gets a simple string or integer value, caching it under an alias.

        Args:
            alias (str): The key to save this value under.
            prompt_message (str, optional): A custom message to display when asking for input.
            value_type (type, optional): The expected type of the value (str or int). Defaults to str.
            force_ask (bool, optional): If True, always prompts the user even if a value is cached.

        Returns:
            The requested value (str or int), or None if input is aborted.
        """
        if value_type not in [str, int]:
            raise ValueError("value_type must be str or int.")

        # 1. Check for a cached value if not forcing a prompt
        if not force_ask and alias in self.saved_paths:
            saved_val = self.saved_paths[alias]
            try:
                # Attempt to cast the saved value to the desired type
                typed_value = value_type(saved_val)
                print(f"Using saved value for '{alias}': {typed_value}")
                return typed_value
            except (ValueError, TypeError):
                print(f"Warning: Saved value for '{alias}' ('{saved_val}') is not a valid {value_type.__name__}. Please re-enter.")

        # 2. Prompt for a new value
        if not prompt_message:
            prompt_message = f"Enter the value for '{alias}'"
            if value_type == int:
                prompt_message += " (must be an integer)"
        
        final_prompt = prompt_message.strip()
        if not final_prompt.endswith(':'):
            final_prompt += ':'
        
        while True:
            try:
                user_input = input(f"{final_prompt} ")
                if value_type == int:
                    # Validate and convert to integer
                    final_value = int(user_input)
                else: # value_type is str
                    final_value = user_input

                # 3. Save and return the new value
                self.saved_paths[alias] = final_value
                print(f"Value for '{alias}' set to: {final_value}")
                self.save_state()
                return final_value

            except ValueError:
                print(f"Invalid input. Please enter a valid integer.")
            except (KeyboardInterrupt, EOFError):
                print("\nInput cancelled.")
                return None

    def _pick_item_interactive(self, mode, prompt_message, start_path_for_session):
        """
        Core interactive picker for directories or files.
        Args:
            mode (str): 'directory' or 'file'.
            prompt_message (str): Message to display to the user.
            start_path_for_session (str): The absolute path to start browsing from.
        """
        self._current_browsing_path = os.path.abspath(start_path_for_session)
        self._print_help(mode)
        print(f"\n{prompt_message}")
        

        selected_item_path = None # Will hold the path of the item if selected

        while True:
            dirs, files = self._display_current_location_and_files(self._current_browsing_path)
            
            base_display_name = os.path.basename(self._current_browsing_path)
            if not base_display_name and os.path.splitdrive(self._current_browsing_path)[1] == os.sep:
                 base_display_name = os.path.normpath(self._current_browsing_path)

            try:
                choice = input(f"Enter command ('h' for help) [{base_display_name or self._current_browsing_path}]> ").strip().lower()
            except EOFError: print("\nInput ended. Quitting picker."); choice = 'q'
            except KeyboardInterrupt: print("\nPicker interrupted. Quitting."); choice = 'q'

            if not choice: continue
            parts = choice.split(); command_full = choice; command_prefix = parts[0]; args = parts[1:]

            if command_prefix.isdigit(): # Navigate into directory by number
                try:
                    dir_index = int(command_prefix) - 1
                    if 0 <= dir_index < len(dirs):
                        self._current_browsing_path = os.path.abspath(os.path.join(self._current_browsing_path, dirs[dir_index]))
                    else: print("Invalid directory number.")
                except ValueError: print("Invalid input. Enter a number for a directory.")
            
            elif mode == 'file' and command_prefix.startswith('f') and command_prefix[1:].isdigit(): # Select file f<num>
                try:
                    file_index = int(command_prefix[1:]) - 1
                    if 0 <= file_index < len(files):
                        selected_item_path = os.path.abspath(os.path.join(self._current_browsing_path, files[file_index]))
                        print(f"Selected file: {selected_item_path}")
                        break # Exit loop
                    else: print("Invalid file number.")
                except ValueError: print("Invalid file selection format (e.g., f1, f2).")

            elif command_prefix == "s": # Select current directory
                selected_item_path = os.path.abspath(self._current_browsing_path)
                if mode == 'directory':
                    print(f"Selected directory: {selected_item_path}")
                elif mode == 'file':
                     # In file mode, 's' selects the current directory, not a file.
                     # The get_file method will handle if this is acceptable or needs re-prompt.
                    print(f"Selected current directory: {selected_item_path}")
                break # Exit loop

            elif command_prefix in ["u", "..", "up"]:
                parent_path = os.path.abspath(os.path.join(self._current_browsing_path, os.pardir))
                if parent_path == self._current_browsing_path: print("Already at the top-most accessible directory.")
                else: self._current_browsing_path = parent_path
            
            elif command_prefix == "save" and args:
                alias_to_save = args[0]
                # 'save' always saves the current browsed directory
                path_to_save_for_alias = os.path.abspath(self._current_browsing_path)
                self.saved_paths[alias_to_save] = path_to_save_for_alias
                print(f"Saved current directory '{path_to_save_for_alias}' as alias '{alias_to_save}'.")
                self.save_state() # Persist this change immediately

            elif command_prefix == "goto" and args:
                alias_to_go = args[0]
                if alias_to_go in self.saved_paths:
                    target_path = self.saved_paths[alias_to_go]
                    if os.path.isdir(target_path): # GOTO only makes sense for directories
                        self._current_browsing_path = target_path
                        print(f"Jumped to alias '{alias_to_go}': {self._current_browsing_path}")
                    else:
                        print(f"Path for alias '{alias_to_go}' ('{target_path}') is not a directory. Cannot goto.")
                else: print(f"Alias '{alias_to_go}' not found.")
            
            elif command_prefix == "list": self.print_saved_paths(verbose=False) # verbose=False to not print file info
            elif command_prefix == "pwd": print(f"Current browsed directory: {os.path.abspath(self._current_browsing_path)}")
            elif command_prefix == "q": selected_item_path = None; print("Picker aborted."); break
            elif command_prefix == "h": self._print_help(mode)
            else: print(f"Unknown command: '{command_full}'. Type 'h' for help.")

        # After loop (selection or quit)
        self._last_browsed_path = self._current_browsing_path # Update last browsed directory
        self.save_state() # Save the state including the new last_browsed_path
        self._current_browsing_path = None # Clear active browsing path
        return selected_item_path


    def _get_path_internal(self, item_type, alias, prompt_message, default_start_path, force_ask):
        """Internal helper for get_directory and get_file."""
        if item_type not in ['directory', 'file']:
            raise ValueError("item_type must be 'directory' or 'file'")

        is_valid_check = os.path.isdir if item_type == 'directory' else os.path.isfile

        if not prompt_message:
            prompt_message = f"Please select or confirm the {item_type} for '{alias}':"

        if not force_ask and alias in self.saved_paths:
            path = self.saved_paths[alias]
            if is_valid_check(path):
                print(f"Using saved {item_type} path for '{alias}': {path}")
                return path
            else:
                print(f"Saved path for '{alias}' ('{path}') is no longer a valid {item_type}. Please re-select.")
        
        # Determine the starting path for the picker session
        start_path_for_session = None
        if default_start_path:
            if default_start_path in self.saved_paths:
                candidate_path = self.saved_paths[default_start_path]
                # If starting from an alias, it should be a directory for browsing
                if os.path.isdir(candidate_path):
                    start_path_for_session = candidate_path
                    print(f"Starting picker at saved alias '{default_start_path}': {start_path_for_session}")
                else: print(f"Warning: Path for alias '{default_start_path}' ('{candidate_path}') is not a browsable directory.")
            elif os.path.isdir(default_start_path):
                start_path_for_session = os.path.abspath(default_start_path)
            else: print(f"Warning: Provided default_start_path '{default_start_path}' is not a directory or known alias.")
        
        if start_path_for_session is None: # Fallback if no valid default_start_path given
            if self._last_browsed_path and os.path.isdir(self._last_browsed_path):
                start_path_for_session = self._last_browsed_path
            else:
                start_path_for_session = self._effective_initial_start_path

        # --- Call the interactive picker ---
        selected_path = self._pick_item_interactive(item_type, prompt_message, start_path_for_session)

        if selected_path:
            # Validate if the selected path is of the correct type
            if not is_valid_check(selected_path):
                print(f"Error: Selected item '{selected_path}' is not a valid {item_type}. Please try again.")
                return None
            
            abs_selected_path = os.path.abspath(selected_path)
            self.saved_paths[alias] = abs_selected_path
            print(f"{item_type.capitalize()} path for '{alias}' set to: {abs_selected_path}")
            self.save_state()
            return abs_selected_path
        return None

    def get_directory(self, alias, prompt_message=None, default_start_path=None, force_ask=False):
        return self._get_path_internal('directory', alias, prompt_message, default_start_path, force_ask)

    def get_file(self, alias, prompt_message=None, default_start_path=None, force_ask=False):
        return self._get_path_internal('file', alias, prompt_message, default_start_path, force_ask)

    def pick_directory(self, prompt_message="Navigate to and select a directory:", start_path=None):
        """Directly invokes the interactive directory picker without aliasing."""
        effective_start = start_path or self._last_browsed_path or self._effective_initial_start_path
        if not os.path.isdir(effective_start): effective_start = os.getcwd()
        return self._pick_item_interactive('directory', prompt_message, effective_start)

    def pick_file(self, prompt_message="Navigate to and select a file:", start_path=None):
        """Directly invokes the interactive file picker without aliasing."""
        effective_start = start_path or self._last_browsed_path or self._effective_initial_start_path
        if not os.path.isdir(effective_start): effective_start = os.getcwd()
        return self._pick_item_interactive('file', prompt_message, effective_start)

    def print_saved_paths(self, verbose=True):
        if not self.saved_paths:
            print("No paths saved yet.")
            return
        
        print("\n--- Saved Paths ---")
        for alias, path in self.saved_paths.items():
            status = ""
            if verbose:
                if os.path.isdir(path): status = "[DIR]"
                elif os.path.isfile(path): status = "[FILE]"
                else: status = "[INVALID/NOT FOUND]"
            print(f"  {alias}: {path} {status}")
        print("-------------------")
        if self._last_browsed_path:
             print(f"Last browsed location: {self._last_browsed_path}")


# --- Example Usage ---
if __name__ == "__main__":
    picker = DirectoryPicker() 

    input1 = picker.get_directory("project_root",
                                  prompt_message="Select your main project root directory:")
    
    if input1: # Only ask for the next input if the first was successful
        input2 = picker.get_file("config_file",
                              prompt_message="Select the main configuration file:",
                              default_start_path="project_root") # Use alias

    print("\n--- Final State ---")
    picker.print_saved_paths()