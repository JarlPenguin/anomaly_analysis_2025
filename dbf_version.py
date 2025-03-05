import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dbf_version.py <input.dbf>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as input_file:
         byte = input_file.read(1)
         print(f"You have a DBF {int.from_bytes(byte)} file.")