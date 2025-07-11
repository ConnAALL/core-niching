import os

def clear_last_line_of_csvs():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(script_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(script_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if lines:
                lines = lines[:-1]  # Remove the last line

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"Cleared last line of: {filename}")

clear_last_line_of_csvs()

