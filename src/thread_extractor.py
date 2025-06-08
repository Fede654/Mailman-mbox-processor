import mailbox
import json
import re
from email.utils import parsedate_to_datetime
from datetime import datetime
from typing import Dict, List, Optional, Any

def clean_subject(subject: str) -> str:
    """Clean and normalize email subject line."""
    if not subject:
        return "No Subject"
    
    # Remove common reply prefixes
    subject = re.sub(r'^(Re:|RE:|Fwd:|FWD:|AW:|Aw:)\s*', '', subject.strip(), flags=re.IGNORECASE)
    
    # Remove extra whitespace
    subject = re.sub(r'\s+', ' ', subject).strip()
    
    return subject or "No Subject"

def extract_message_id(message_id: str) -> Optional[str]:
    """Extract clean message ID from header."""
    if not message_id:
        return None
    
    # Remove angle brackets if present
    match = re.search(r'<([^>]+)>', message_id)
    return match.group(1) if match else message_id.strip()

def build_thread_tree(messages: Dict[str, Any]) -> Dict[str, List[str]]:
    """Build parent-child relationships between messages."""
    children = {mid: [] for mid in messages}
    
    for mid, message in messages.items():
        in_reply_to = message.get('In-Reply-To')
        references = message.get('References', '')
        
        # Try In-Reply-To first
        parent_mid = None
        if in_reply_to:
            parent_mid = extract_message_id(in_reply_to)
        
        # If no In-Reply-To, try last reference
        if not parent_mid and references:
            ref_list = re.findall(r'<([^>]+)>', references)
            if ref_list:
                parent_mid = ref_list[-1]
        
        if parent_mid and parent_mid in messages:
            children[parent_mid].append(mid)
    
    return children

def get_thread_messages(root_mid: str, messages: Dict[str, Any], children: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Recursively collect all messages in a thread."""
    thread_messages = []
    
    def collect_messages(mid: str, depth: int = 0):
        if mid in messages:
            msg_data = messages[mid]
            thread_messages.append({
                'message_id': mid,
                'subject': msg_data.get('Subject', ''),
                'from': msg_data.get('From', ''),
                'date': msg_data.get('Date', ''),
                'date_parsed': msg_data.get('date_parsed'),
                'depth': depth
            })
            
            # Sort children by date before recursing
            child_mids = children.get(mid, [])
            child_messages = []
            for c_mid in child_mids:
                if c_mid in messages:
                    child_messages.append((messages[c_mid].get('date_parsed'), c_mid))
            
            child_messages.sort(key=lambda x: (x[0] is None, x[0]))
            
            for _, c_mid in child_messages:
                collect_messages(c_mid, depth + 1)
    
    collect_messages(root_mid)
    return thread_messages

def extract_threads_to_json(mbox_path: str, output_path: str = 'threads.json'):
    """Extract thread information from mbox file and save to JSON."""
    
    # Parse all messages
    mbox = mailbox.mbox(mbox_path)
    messages = {}
    
    print(f"Reading messages from {mbox_path}...")
    
    for message in mbox:
        mid = extract_message_id(message.get('Message-ID', ''))
        if mid:
            # Parse date
            date_str = message.get('Date', '')
            date_parsed = None
            if date_str:
                try:
                    date_parsed = parsedate_to_datetime(date_str)
                except Exception:
                    pass
            
            messages[mid] = {
                'Subject': message.get('Subject', ''),
                'From': message.get('From', ''),
                'Date': date_str,
                'In-Reply-To': message.get('In-Reply-To', ''),
                'References': message.get('References', ''),
                'date_parsed': date_parsed
            }
    
    print(f"Found {len(messages)} messages")
    
    # Build thread relationships
    children = build_thread_tree(messages)
    
    # Find root messages (not replied to by any other message)
    all_children = set()
    for child_list in children.values():
        all_children.update(child_list)
    
    roots = [mid for mid in messages if mid not in all_children]
    print(f"Found {len(roots)} thread roots")
    
    # Sort roots by date
    roots_with_dates = []
    for mid in roots:
        message = messages[mid]
        date_parsed = message.get('date_parsed')
        roots_with_dates.append((date_parsed, mid))
    
    roots_with_dates.sort(key=lambda x: (x[0] is None, x[0]))
    
    # Build final thread structure
    threads_data = {
        'metadata': {
            'extracted_at': datetime.now().isoformat(),
            'source_file': mbox_path,
            'total_messages': len(messages),
            'total_threads': len(roots)
        },
        'threads': []
    }
    
    for i, (start_date, root_mid) in enumerate(roots_with_dates, 1):
        root_message = messages[root_mid]
        cleaned_subject = clean_subject(root_message.get('Subject', ''))
        
        # Count total messages in thread
        thread_messages = get_thread_messages(root_mid, messages, children)
        
        thread_data = {
            'thread_id': i,
            'root_message_id': root_mid,
            'subject': cleaned_subject,
            'subject_raw': root_message.get('Subject', ''),
            'start_date': start_date.isoformat() if start_date else None,
            'start_date_raw': root_message.get('Date', ''),
            'starter_from': root_message.get('From', ''),
            'message_count': len(thread_messages),
            'messages': thread_messages
        }
        
        threads_data['threads'].append(thread_data)
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(threads_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Thread data saved to {output_path}")
    print(f"Summary: {len(roots)} threads, {len(messages)} total messages")
    
    return threads_data

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python thread_extractor.py <mbox_path>")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    extract_threads_to_json(mbox_path)