"""
takes all uploaded and modified files and if they are in the right format,
 they are converted to json and uploaded to elastic
"""
import sys
import convert_md_to_json_git_workflow
import load_jsons_to_elasticsearch_git_workflow

# process all files as arguments via for loop
for file in sys.argv[1:]:
    print(f"processing file: '{file}'.")
    # in case the file is right converts it into json
    if (
        file.endswith("md")
        and file.startswith("_index") is False
        and file not in ["LICENSE.md", "README.md"]
    ):
        print(f"file: '{file}' will be converted to JSON.")
        file_as_json = convert_md_to_json_git_workflow.convert_file(file)
       

        print(f"file: '{file}' will be uploaded to JSON.")
        elastic_response = (load_jsons_to_elasticsearch_git_workflow.upload_to_elastic(file_as_json))

        if elastic_response in ["created", "updated"]:
            print(f"file: '{file}' is uploaded to elastic.")
        else:
            print(f"file: '{file}' hasn't been able to upload.")

    # the converted json uploads to elastic
    else:
        print(f"file: '{file}' is not right to convert.")
