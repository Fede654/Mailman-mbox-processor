import mailbox
import re
from email.utils import parsedate_to_datetime
import os

def main(mbox_path, output_dir='output/'):
    # Open and parse the mbox file
    mbox = mailbox.mbox(mbox_path)
    messages = {}
    for message in mbox:
        mid = message['Message-ID']
        if mid:
            messages[mid] = message

    # Build the parent-child relationships
    children = {mid: [] for mid in messages}
    for mid, message in messages.items():
        in_reply_to = message['In-Reply-To']
        if in_reply_to:
            match = re.search(r'<([^>]+)>', in_reply_to)
            if match:
                parent_mid = match.group(1)
                if parent_mid in messages:
                    children[parent_mid].append(mid)

    # Identify root messages (those not replied to)
    all_children = set()
    for child_list in children.values():
        all_children.update(child_list)
    roots = [mid for mid in messages if mid not in all_children]

    # Sort roots by date
    roots_with_dates = []
    for mid in roots:
        message = messages[mid]
        date_str = message['Date']
        date = None
        if date_str:
            try:
                date = parsedate_to_datetime(date_str)
            except Exception:
                pass
        roots_with_dates.append((date, mid))
    roots_with_dates.sort(key=lambda x: (x[0] is None, x[0]))

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write each thread to its own file
    for i, (date, mid) in enumerate(roots_with_dates, start=1):
        root_message = messages[mid]
        subject = root_message['Subject'] or 'No Subject'
        safe_subject = re.sub(r'[^\w\s-]', '', subject).strip().replace(' ', '_')
        filename = f"{i:03d}_{safe_subject}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            if date:
                f.write(f"Thread started on {date}:\n")
            else:
                f.write("Thread started on unknown date:\n")
            print_thread(mid, messages, children, file=f)

def print_thread(mid, messages, children, indent=0, file=None):
    # Print the current message with appropriate indentation
    message = messages[mid]
    subject = message['Subject'] or 'No Subject'
    file.write('  ' * indent + subject + '\n')
    
    # Sort and print child messages
    child_mids = children[mid]
    child_messages = []
    for c in child_mids:
        c_message = messages[c]
        date_str = c_message['Date']
        date = None
        if date_str:
            try:
                date = parsedate_to_datetime(date_str)
            except Exception:
                pass
        child_messages.append((date, c))
    child_messages.sort(key=lambda x: (x[0] is None, x[0]))
    for date, c in child_messages:
        print_thread(c, messages, children, indent + 1, file=file)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python thread_saver.py <mbox_path>")
        sys.exit(1)
    mbox_path = sys.argv[1]
    main(mbox_path)