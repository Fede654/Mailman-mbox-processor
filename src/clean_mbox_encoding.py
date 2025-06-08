import re

def clean_mbox(input_path, output_path):
    with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
        for line in infile:
            if line.startswith(b'From '):
                # Replace non-ASCII characters in "From " lines with ASCII equivalents or remove them
                cleaned_line = re.sub(rb'[^\x00-\x7F]', b'', line)
                outfile.write(cleaned_line)
            else:
                # Write other lines as-is (they’ll be handled by UTF-8 encoding)
                outfile.write(line)

# Example usage
input_mbox = "44net.mbox"
output_mbox = "44net-mailman.mbox"
clean_mbox(input_mbox, output_mbox)

print(f"Cleaned mbox file written to {output_mbox}")