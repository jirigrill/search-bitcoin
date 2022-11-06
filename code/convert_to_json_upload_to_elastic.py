"""
takes all uploaded and modified files and if they are in the right format,
 they are converted to json and uploaded to elastic
"""
import sys
import convert_md_to_json_git_workflow

ROOT_FOLDER = "search-bitcoin"

# process all files as arguments via for loop
for file in sys.argv[1:]:
    print(f"processing file: '{file}'.")
    print(f"markdown file: {file.rsplit('/', maxsplit=1)[0]}")
    # in case the file is right converts it into json
    if (
        file.endswith("md")
        and file.startswith("_index") is False
        and file not in ["LICENSE.md", "README.md"]
    ):
        print(f"file: '{file}' will be converted to JSON.")
        file_as_json = convert_md_to_json_git_workflow.convert_file(
            root_folder=ROOT_FOLDER, file_path=file, markdown_file=file.rsplit('/', maxsplit=1)[-1]
        )
    # the converted json uploads to elastic
    else:
        print(f"file: '{file}' is not right to convert.")
