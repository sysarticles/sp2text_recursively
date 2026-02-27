import sys

def format_text_file(file_path):
    """
    Reads a text file, replaces periods with a period followed by a newline,
    and writes the modified content back to the same file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        modified_content = content.replace(".", ".\n")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        print(f"File formatted successfully: {file_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cevir.py <file_path>")
    else:
        format_text_file(sys.argv[1])
