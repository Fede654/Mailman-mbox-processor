import re
import json
from datetime import datetime

# Custom parser function (simplified example based on your output)
def parse_mbox_to_threads(mbox_path):
    threads = []
    current_thread = None
    
    with open(mbox_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            # Match timestamp line (adjust regex as needed for your format)
            time_match = re.match(r'Thread started on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}):', line)
            if time_match:
                if current_thread:  # Save previous thread
                    threads.append(current_thread)
                # Start new thread with timestamp
                timestamp = time_match.group(1)
                current_thread = {"start_time": timestamp, "subject": ""}
            elif current_thread and line.strip() and not current_thread["subject"]:
                # Assume next non-empty line after timestamp is the subject
                current_thread["subject"] = line.strip()
        
        # Append the last thread
        if current_thread:
            threads.append(current_thread)
    
    return threads

# Main execution
mbox_file = "44net@mailman.ampr.org-2025-06.mbox"
output_json = "threads.json"

# Parse threads and write to JSON
threads_data = parse_mbox_to_threads(mbox_file)
with open(output_json, 'w', encoding='utf-8') as json_file:
    json.dump(threads_data, json_file, indent=4, ensure_ascii=False)

print(f"Thread data written to {output_json}")
