import argparse
import os
import json
import re
from datetime import datetime

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process an mbox file and extract thread information to a JSON file.")
    parser.add_argument("mbox_path", help="Path to the mbox file to process.")
    return parser.parse_args()

def check_file_access(mbox_path):
    """Check if the mbox file exists and is readable."""
    if not os.path.isfile(mbox_path):
        raise FileNotFoundError(f"The file {mbox_path} does not exist.")
    if not os.access(mbox_path, os.R_OK):
        raise PermissionError(f"Cannot read the file {mbox_path}.")

def parse_mbox_to_threads(mbox_path):
    """Parse the mbox file and extract thread information."""
    threads = []
    current_thread = None
    with open(mbox_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            # Match the timestamp line (adjust regex if your format differs)
            time_match = re.match(r'Thread started on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}):', line)
            if time_match:
                if current_thread:
                    threads.append(current_thread)
                timestamp = time_match.group(1)
                current_thread = {"start_time": timestamp, "subject": ""}
            elif current_thread and line.strip() and not current_thread["subject"]:
                current_thread["subject"] = line.strip()
        if current_thread:
            threads.append(current_thread)
    return threads

def write_threads_to_json(threads, output_json):
    """Write the thread information to a JSON file."""
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(threads, json_file, indent=4, ensure_ascii=False)

def main():
    """Main function to orchestrate the script."""
    args = parse_arguments()
    mbox_path = args.mbox_path
    output_json = "threads.json"
    try:
        check_file_access(mbox_path)
        threads = parse_mbox_to_threads(mbox_path)
        write_threads_to_json(threads, output_json)
        print(f"Thread data written to {output_json}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()