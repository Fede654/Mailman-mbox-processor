# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Python scripts for processing Mailman mbox archive files. The main functionality is to parse mbox files, extract email messages, build thread relationships based on message headers, and export organized thread data.

## Core Architecture

The codebase consists of several iterative versions of email processing scripts:

- **thread_saver.py**: Original mbox parser using Python's `mailbox` module
- **thread_saver-2.py**: Improved version with custom mbox parsing to handle encoding issues
- **thread_saver-3.py** and **thread_saver-4.py**: Further iterations (need inspection)
- **clean_mbox_encoding.py**: Utility to clean non-ASCII characters from mbox "From " lines

### Email Threading Logic

All thread_saver variants follow this pattern:
1. Parse mbox file and extract messages by Message-ID
2. Build parent-child relationships using In-Reply-To headers
3. Identify root messages (threads with no parent)
4. Sort threads chronologically by date
5. Export threads to individual text files with indented structure

### Key Data Structures

- `messages`: Dict mapping Message-ID to email message objects
- `children`: Dict mapping parent Message-ID to list of child Message-IDs
- `roots`: List of Message-IDs that start threads (no parent)

## Common Commands

```bash
# Run the main thread saver
python src/thread_saver.py <mbox_path>

# Run improved version with custom parsing
python src/thread_saver-2.py <mbox_path>

# Clean encoding issues in mbox file
python src/clean_mbox_encoding.py
```

## File Processing Flow

1. **Input**: Mailman mbox archive files (e.g., `44net-mailman.mbox`)
2. **Processing**: Parse messages, build thread relationships, sort by date
3. **Output**: Individual text files per thread in `output/` directory with format `001_Subject_Line.txt`

## Encoding Considerations

Mailman mbox files may contain non-ASCII characters in "From " separator lines, which can cause parsing issues. Use `clean_mbox_encoding.py` to preprocess problematic files before running thread extraction.