"""
takes all uploaded and modified files and if they are in the right format,
 they are converted to json and uploaded to elastic
"""
import sys

# process all files as arguments via for loop
for file in sys.argv[1:]:
    print(f"processing file: '{file}'")
    # in case the file is right converts it into json
    if (
        file.endswith("md")
        and file.startswith("_index") is False
        and file not in ["LICENSE.md", "README.md"]
    ):
        print(f"file: '{file}' will be converted.")
    # the converted json uploads to elastic
    else:
        print(f"file: '{file}' is not right to convert.")
