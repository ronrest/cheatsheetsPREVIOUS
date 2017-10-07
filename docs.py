from __future__ import print_function, division, unicode_literals
import shutil
import re
import os
from jinja2 import Environment, select_autoescape, FileSystemLoader # PackageLoader


# ==============================================================================
#                                                                 MAYBE_MAKE_DIR
# ==============================================================================
def maybe_make_dir(path):
    """ Checks if a directory path exists on the system, if it does not, then
        it creates that directory (and any parent directories needed to
        create that directory)
    """
    if not os.path.exists(path):
        os.makedirs(path)


# ==============================================================================
#                                                              MAYBE_MAKE_PARDIR
# ==============================================================================
def maybe_make_pardir(file):
    """ Takes a path to a file, and creates the necessary directory structure
        on the system to ensure that the parent directory exists (if it does
        not already exist)
    """
    pardir = os.path.dirname(file)
    if pardir.strip() != "": # ensure pardir is not an empty string
        if not os.path.exists(pardir):
            os.makedirs(pardir)


# ==============================================================================
#                                                                       FILE2STR
# ==============================================================================
def file2str(f):
    with open(f, "r") as textFile:
        return textFile.read()


# ==============================================================================
#                                                                       STR2FILE
# ==============================================================================
def str2file(s, file):
    maybe_make_pardir(file)
    with open(file, mode="w") as textFile:
        textFile.write(s)


# ==============================================================================
#                                                      PARSE_INDEX_SECTIONS_FILE
# ==============================================================================
def parse_index_sections_file(file):
    """ Given a file containing sections and groups and items it returns a
        tuple of three things:

        (document_title, output_dir, sections_list_of_dictionaries)


    The file it reads from should be formatted as follows:

    --------------------------------------------
    My Cheatchseets Title
    /output/dir

    Linear Algebra
        Vectors
            linalg/simple_vectors
            linalg/vector_dot_products
        Matrices
            linalg/simple_matrices
            linalg/matrix_multiplication
            linalg/matrix_and_vectors
    Algebra
        Basics
            alg/polynomials
            alg/quadratic_functions

    --------------------------------------------
    NOTE: - The first line = Title for cheatsheets
          - The second line = the output directory (leave blank line to have current dir as output)
          - sections must be flush against left border
          - groups within a section MUST be indented EXACTLY 4 lines
          - items within groups MUST be indented EXACTLY 8 lines

    It returns a list of dictionaries:
    --------------------------------------------
    [
        # SECTION 0
        {'title': 'Linear Algebra',
        'groups': [
            # GROUP 0
            {'title': 'Vectors',
            'files': [
                # FILE 0
                {'name': 'simple_vectors',
                'out_file': 'linalg/simple_vectors.html',
                'source_file': '/input/dir/linalg/simple_vectors'},

                # FILE 1
                {'name': 'vector_dot_products',
                'out_file': 'linalg/vector_dot_products.html',
                'source_file': '/input/dir/linalg/vector_dot_products'}
                ]},

            # GROUP 1
            {'title': 'Matrices',
            'files': [
                # FILE 0
                {'name': 'simple_matrices',
                'out_file': 'linalg/simple_matrices.html',
                'source_file': '/input/dir/linalg/simple_matrices'},

                # FILE 1
                {'name': 'matrix_multiplication',
                'out_file': 'linalg/matrix_multiplication.html',
                'source_file': '/input/dir/linalg/matrix_multiplication'},

                # FILE 2
                {'name': 'matrix_and_vectors',
                'out_file': 'linalg/matrix_and_vectors.html',
                'source_file': '/input/dir/linalg/matrix_and_vectors'}
                ]}
        ]},

        # SECTION 1
        {'title': 'Algebra',
        'groups': [
            # GROUP 0
            {'title': 'Basics'
            'files': [
                # FILE 0
                {'name': 'polynomials',
                'out_file': 'alg/polynomials.html',
                'source_file': '/input/dir/alg/polynomials'},

                # FILE 1
                {'name': 'quadratic_functions',
                'out_file': 'alg/quadratic_functions.html',
                'source_file': '/input/dir/alg/quadratic_functions'}
                ]}
        ]}
    ]
    --------------------------------------------

    # ACCESSING THE DATA:

    sid = 1 # Section id
    gid = 0 # groud id
    iid = 1 # item id
    Accessing the s'th section                = sections[sid]
    Accessing the s'th section title          = sections[sid]["title"]
    Accessing the groups list of s'th section = sections[sid]["groups"]

    Accessing the g'th group of s'th section  = sections[sid]["groups"][gid]
    Accessing the title of g'th group         = sections[sid]["groups"][gid]["title"]

    Accessing the file name of i'th item      = sections[sid]["groups"][gid]["files"][iid]["name"]
    Accessing the source file of i'th item    = sections[sid]["groups"][gid]["files"][iid]["source_file"]
    Accessing the output file of i'th item    = sections[sid]["groups"][gid]["files"][iid]["out_file"]
    """
    n_header_lines = 2  # number of lines dedicated to metadata in cht file
    project_dir = os.path.dirname(file)

    # Split the file into lines
    lines = file2str(file).splitlines()

    # Cheatsheets Main title
    title = lines[0].strip()

    # OUTPUT DIRECTORY - removing redundant separators and handling path
    # relative to the project directory.
    out_dir = lines[1].strip()
    out_dir = os.path.normpath(os.path.join(project_dir, out_dir))

    sections = []
    for line in lines[n_header_lines:]:
        # Match line to either a section title, a group title, or a group item
        section_match = re.search("^(\S+.*)", line)
        group_match = re.search("^\s{4}(\S+.*)", line)
        group_item_match = re.search("^\s{8}(\S+.*)", line)

        # IS A SECTION TITLE
        if section_match:
            # Get the section title, and add a section to the dict
            section_title = section_match.groups()[0]
            sections.append({"title": section_title, "groups":[]})

        # IS A GROUP TITLE
        elif group_match:
            # Get the group title, and append a group to the dict
            group_title = group_match.groups()[0]
            sections[-1]["groups"].append({"title": group_title, "files": []})

        # IS A GROUP ITEM
        elif group_item_match:
            # Get the relative filepath to the source file for this item
            source_file = group_item_match.groups()[0]
            file_name = os.path.basename(source_file)

            # Clean up filepaths to source and output file
            out_file = os.path.normpath(os.path.join(source_file+".html"))
            source_file = os.path.normpath(os.path.join(project_dir, source_file))
            sections[-1]["groups"][-1]["files"].append({"name":file_name, "source_file":source_file, "out_file":out_file})

        # Skip over blank lines
        elif line.strip() == "":
            continue

        # Error handling of format
        else:
            assert True, "There is something wrong with the formatting of you cheatsheets file, check the indentation"

    return title, out_dir, sections


# ==============================================================================
#                                                                     PARSE_PAGE
# ==============================================================================
def parse_page(source_file, out_file):
    # TODO: Parse the source_file and create its own html page
    pass


# ==============================================================================
#                                                            CREATE HTML CONTENT
# ==============================================================================
def generate_html(sections, out_dir, title="My Cheatsheets"):
    """ Given a list of dictionaries specifying the sections and groups and
        items, and an output dir, it generates the necessary html
    """
    # TODO: Set filepaths of template to be relative to this script file
    #       explicitly.
    index_title = title
    html_template = file2str("templates/index.html")
    nav_items_template = file2str("templates/nav_item.html")
    section_template = file2str("templates/section.html")
    group_template = file2str("templates/group.html")
    group_item_template = file2str("templates/group_item.html")

    # Iterate through each section
    nav_items_str = ""
    all_sections_str = ""
    for section in sections:
        section_title = section["title"]
        # print(section_title)

        # Iterate through each group in section
        all_groups_str = ""
        for group in section["groups"]:
            group_title = group["title"]
            # print(" -", group_title)

            # Iterate through each item in group
            all_items_str = ""
            for source_file, out_file in group["files"]:
                item_title = os.path.basename(source_file).capitalize()
                #print("   - ", item_title, "--", source_file)

                # PARSE PAGE - from source file to its own html page
                parse_page(source_file, out_file)

                all_items_str += "\n" + group_item_template.format(item_url=out_file, item_title=item_title)

            all_groups_str += "\n" + group_template.format(group_title=group_title, group_items=all_items_str)
        all_sections_str += "\n" + section_template.format(section_title=section_title, section_id=section_title, section_content=all_groups_str)
        nav_items_str += "\n" + nav_items_template.format(section_title=section_title, section_id=section_title)

    html_str = html_template.format(index_title=index_title, sections=all_sections_str, nav_items=nav_items_str)

    # Move files to apropriate direcoty
    maybe_make_pardir(out_dir)
    str2file(html_str, os.path.join(out_dir, "index.html"))
    shutil.copy2("static/style.css", os.path.join(out_dir, "style.css"))


# ==============================================================================
#                                                             PREPARE_OUTPUT_DIR
# ==============================================================================
def prepare_output_dir(out_dir):
    """ Creates the directory structure for the output, including css files """
    maybe_make_dir(out_dir)
    shutil.copy2("static/style.css", os.path.join(out_dir, "style.css"))


# ##############################################################################
#                                                                           MAIN
# ##############################################################################
if __name__ == '__main__':
    sections_file = "example1/sections.cht"
    index_title, out_dir, sections = parse_index_sections_file(sections_file)
    # generate_html(sections, out_dir=out_dir, title=index_title)

    # Jinja Templating Environment
    env = Environment(
        loader=FileSystemLoader('templates', encoding='utf-8'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Create necessary file structure for output project
    prepare_output_dir(out_dir)

    # GENERATE INDEX PAGE
    index_title, out_dir, sections = parse_index_sections_file(sections_file)
    template = env.get_template('index.html')
    index_page = template.render(index_title=index_title, nav_items="NAV ITEMS", sections=sections)
    str2file(index_page, os.path.join(out_dir, "index.html"))

