from __future__ import print_function, division, unicode_literals
import shutil
import re
import os


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
    /my/output/dir

    Lnear Algebra
        Vectors
            simple_vectors
            vector_dot_products
        Matrices
            simple_matrices
            matrix_multiplication
            matrix_and_vectors
    Algebra
        Basics
            polynomials
            quadratic_functions

    --------------------------------------------
    NOTE: - The first line = Title for cheatsheets
          - The second line = the output directory (leave blank line to have current dir as output)
          - sections must be flush against left border
          - groups within a section MUST be indented EXACTLY 4 lines
          - items within groups MUST be indented EXACTLY 8 lines

    It returns a list of dictionaries:
    --------------------------------------------
    [{'title': 'Lnear Algebra',
      'groups': [{'title': 'Vectors',
                   'files': [('simple_vectors', 'simple_vectors.html'),
                             ('vector_dot_products', 'vector_dot_products.html')],
                             },
                  {'title': 'Matrices',
                   'files': [('simple_matrices', u'simple_matrices.html'),
                              ('matrix_multiplication', u'matrix_multiplication.html'),
                              ('matrix_and_vectors', u'matrix_and_vectors.html')]
                              }
                ]
     },
     {'title': 'Algebra',
      'groups': [{'title': 'Basics',
                  'files': [('polynomials', u'polynomials.html'),
                            ('quadratic_functions', u'quadratic_functions.html')],
                }],
     }]
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

    Accessing the source file of i'th item    = sections[sid]["groups"][gid]["files"][iid][0]
    Accessing the output file of i'th item    = sections[sid]["groups"][gid]["files"][iid][1]
    """
    n_header_lines = 2
    s_raw = file2str(file).splitlines()
    title = s_raw[0].strip()
    out_dir = s_raw[1].strip()

    line = s_raw[2]

    sections = []
    for line in s_raw[n_header_lines:]:
        section_match = re.search("^(\S+.*)", line)
        group_match = re.search("^\s{4}(\S+.*)", line)
        group_item_match = re.search("^\s{8}(\S+.*)", line)

        if section_match:
            section_title = section_match.groups()[0]
            sections.append({"title": section_title, "groups":[]})
        elif group_match:
            group_title = group_match.groups()[0]
            sections[-1]["groups"].append({"title": group_title, "files": []})
        elif group_item_match:
            source_file = group_item_match.groups()[0]
            sections[-1]["groups"][-1]["files"].append(make_source_output_pair(source_file))
        elif line.strip() == "":
            continue
        else:
            assert True, "There is something wrong with the formatting of you cheatsheets file, check the indentation"

    # TODO: Set output dir to be relative to file if it does not start
    # with a "/"
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



if __name__ == '__main__':
    sections_file = "sections.cht"
    index_title, out_dir, sections = parse_index_sections_file(sections_file)
    generate_html(sections, out_dir=out_dir, title=index_title)
