from textwrap import indent
import markdown
import json
from bs4 import BeautifulSoup
import html
import os
import re

LANGUAGE_CODE_DICT = '{"en": "english", "es": "spanish", "pt": "portugese", "de": "german", "it": "italian"}'
LANGUAGE_CODE_DICT = json.loads(LANGUAGE_CODE_DICT)

INFO_DICT = '{"name": "author", "nombre": "author", "topic": "topic", "tema": "topic", "location": "location", "locación": "location", \
    "date": "date", "día": "date", "video": "video_link", "vídeo": "video_link", "slides": "slides_link", "diapositivas": "slides_link" }'

INFO_DICT = json.loads(INFO_DICT)

file_path = ''

def process_table(list_strings):
    """
    Takes list of strings representing header table in markdown file and returns it as dictionary
    """
    table_content_json = json.dumps(list_strings, separators=(',', ':')).strip().replace(':','": "')[1:-1]
    table_content_dict = json.loads('{'+table_content_json+'}')
    table_content_dict = {x:table_content_dict[x].strip() for (x,_) in table_content_dict.items()}

    return table_content_dict


def get_content_pointers(html_string):
    """
    Parses and returns pointer for individual content parts
    """
    info_starts_at = [m.start() for m in re.finditer('<hr />', html_string)][1]
    content_starts_at = [m.start() for m in re.finditer('<h1>', html_string)][0]

    return info_starts_at, content_starts_at


def parse_info_part(html_string, info_starts_at, content_starts_at):
    """
    Takes html as string, parse a part between <hr /> and <h1> and returns it as html
    """

    info_part = html_string[info_starts_at:content_starts_at]
    info_part_html =  BeautifulSoup(info_part, features="html.parser")

    info_part_dict = {}

    for record in info_part_html.find_all('p'):
        row = record.get_text()
        # example of the record: "Name: Andrew Poelstra"
        # check whether 1st word of the row is key in INFO_DICT -> this will tell whether we can assign it according to the dict or not
        first_word_as_info_key = row.split(" ")[0].strip(":").lower()
        possible_value = " ".join(row.split(" ")[1:])

        if first_word_as_info_key in INFO_DICT:
            info_part_dict[INFO_DICT[first_word_as_info_key]] = possible_value

        # check whether record contains hyperlink -> in case yes, it is added into array of key other_links
        else:
            if "http://" in row or "https://" in row:
                # check if markdown_file_as_json already contains key "other links" if not its created
                if "other_links" in info_part_dict:
                    info_part_dict["other_links"].append(row)
                else:
                    info_part_dict["other_links"] = [row]

    return info_part_dict


def get_language_code(language):
    """
    Returns language code based on provided language. By default it sets up to 'en'
    """
    language_code = 'en'

    for key in LANGUAGE_CODE_DICT.keys():
        if language == LANGUAGE_CODE_DICT[key]:
            language_code = key

    return language_code


def define_language(file_path):
    """
    Defines language of the transcript
    """
    try:
        language_code = [code_candidate.lower() for code_candidate in file_path.split('.') if len(code_candidate) == 2 and code_candidate.lower() != 'md'][0]
        language = LANGUAGE_CODE_DICT[language_code]
    except:
        # beacuse file name doesnt contain language code setting up English as default
        language_code = 'en'
        language = 'English'

    return language


def standardise_date(date):
    """
    TODO Returns standardised date in format 'YYYY-MM-DD' for given date
    """
    standardised_date = True
    return standardised_date


def get_btctranscript_link(file_path, language_code):
    """
    Returns https://btctranscripts.com link for given file_path
    """
    domain = 'https://btctranscripts.com'
    wo_local_path = file_path.split('original_markdowns/')[1]
    transcript_path = wo_local_path.split('.')[0]

    if language_code != 'en':
        btctranscripts_link = domain+'/'+language_code+'/'+transcript_path
    else:
        btctranscripts_link = domain+'/'+transcript_path

    return btctranscripts_link

def convert_file(markdown_file, file_path):
    """
    Takes markdown file and converts it into valid json
    """
    markdown_file_as_json = {}
    html_string = markdown.markdown(markdown_file)
    soup = BeautifulSoup(html_string, features="html.parser")

    # parsing first <p></p> to get table items from markdown file
    table_content_list = soup.p.contents[0].split('\n')
    table_content_dict = process_table(table_content_list)

    # adding author to the table dict
    # as default it takes the first part from transcript title
    # later if in "info part" is author clearly defined its updated
    table_content_dict["author"] = table_content_dict["title"].split("-")[0].strip()

    # table content was parsed so its possible to append into markdown_file_as_json
    markdown_file_as_json.update(table_content_dict)

    # setting up English as default language and update it in case file name contains language abbreviation
    # according to language dict
    markdown_file_as_json["language"] = define_language(file_path)

    # setup content pointers
    info_starts_at, content_starts_at = get_content_pointers(html_string)

    # parse the part between <hr/> and first <h1> -> it is the part where author, video link etc is - lets call it info
    info_part_json = parse_info_part(html_string, info_starts_at, content_starts_at)

    # contacetating info_part_json into markdown_file_as_json
    markdown_file_as_json.update(info_part_json)

    # original script which parsed the "content" part which resulted into "<h1>chapter title<h/1>": [<p>chapter content</p>]
    """
    # parsing "content" part
    # value between <h1></h1> is dict key and value between <p><p1> is dict value
    content_json = {}
    for chapter in soup.prettify().split('<h1>')[1:]:
        print(chapter)
        chapter_title = html.unescape(chapter.strip().partition('\n')[0])
        chapter_content = []
        chapter_text = chapter.split('</h1>')[1].replace('</p>','').replace('\n','').split('<p>')
        for paragraph in chapter_text:
            if len(paragraph) > 0:
                chapter_content.append(paragraph.strip())

    # TODO how to parse and store multi-line code snippets?
    # At the moment script produces one long string for code and doesnt reflect new lines in the code snippets

    # TODO is it necessary to do something in case if chapter_text contains HTML list <ul><li>...</li><li>...</li></ul> ?

    # TODO in '2022-03-03-sanket-kanjalkar-miniscript.md' in chapter text the script produces &lt;revocationpubkey&gt
    # instead of <revocationpubkey> -> should it be solved or not?

        content_json[chapter_title] = chapter_content

    # adding chapter content to markdown_file_as_json
    markdown_file_as_json["content"] = content_json
    """

    # new version which parses the "content" part and store it as "content": {<h1>chapter1 title</h1> <p>content of chapter1</p> <h1> chapter2 title</h1> <p>content of chapter2</p>}
    # everything after first <h1> is considered as content
    # content_starts_at = html_string.find('<h1>')
    content_part = html_string[content_starts_at:]

    # adding chapter content to markdown_file_as_json
    markdown_file_as_json["content"] = content_part

    # adding link to bitcoin transcript page
    markdown_file_as_json["btctranscripts_link"] = get_btctranscript_link(file_path, get_language_code(markdown_file_as_json["language"]))

    return markdown_file_as_json

# iterates over *.md files in processed_files directory and adds them to index
for path, subdirs, files in os.walk('../data/original_markdowns/'):
    for file in files:
        if file.endswith('md') and file.startswith('_index')==False:
            file_path = path + os.path.sep + file
            with open(file_path, 'r') as f:
                text = f.read()
                file_name = file
            # storing final file as json
            final_json = json.dumps(convert_file(text, file_path), ensure_ascii=False)

            # at first split file path by '.' and selects only string > 2 to avoid .md and language code (ie .es)
            # from that selection we will only the last part to ensure that file name is in selection
            # that selection is split by '/' and select only last part to ensure that proper file name is selected
            # as the last step language is attached to the end of file_name
            #
            # source: '/Users/jiri.grill/personal_projects/search-bitcoin/data/original_markdowns/advancing-bitcoin/2019/2019-02-07-matt-corallo-rust-lightning.md'
            # after fist step: /Users/jiri.grill/personal_projects/search-bitcoin/data/original_markdowns/advancing-bitcoin/2019/2019-02-07-matt-corallo-rust-lightning
            # after second step: 2019-02-07-matt-corallo-rust-lightning
            file_name  = [file_name.lower() for file_name in file_path.split('.') if len(file_name) > 2][-1].split('/')[-1]

            file_name = file_name+'-'+get_language_code(json.loads(final_json)['language'])

            with open(f"/Users/jiri.grill/personal_projects/search-bitcoin/data/processed_files/{file_name}.json", "w") as outfile:
                outfile.write(final_json)