from support.edi.templates import generic

# Responsible for keeping track of installed templates


class Template_List(list):
    def append(self, obj : object):
        super().append(obj)


template_list = Template_List()


def clean_head(value : bytes):
    return value.strip(b' \t\n\r\v\f')


def discover_all_sections(start_head : bytes, end_head : bytes, bytes_list : list):
    found_list = list()
    # looping until all groups are found and added to list
    found = False
    start_i = 0
    offset = 0
    while not found:
        start_idx = None
        end_idx = None
        # TODO: Lots of integrity and error handling
        found_head = False
        for i, section in enumerate(bytes_list[start_i:]):
            if clean_head(section[0]) == start_head:
                start_idx = i + offset
                found_head = True
            elif clean_head(section[0]) == end_head and found_head:
                end_idx = i + offset
                break
        if start_idx != None and end_idx != None:
            start_i = start_idx + 1
            offset += start_i
            found_list.append(bytes_list[start_idx:end_idx + 1])
        else:
            found = True
    return found_list