# -*- coding: utf-8 -*-


import os
import xml.etree.ElementTree


ROOT = os.path.dirname(os.path.abspath(__file__))


_TYPE_CODE = dict(
    B='browser',
    C='link, bookmark, server checking',
    D='downloading tool',
    P='proxy server, web filtering',
    R='robot, crawler, spider',
    S='spam or bad bot',
)


def parse():
    file = os.path.join(ROOT, 'allagents.xml')
    root = xml.etree.ElementTree.parse(file).getroot()

    ua = dict()
    for element in root:
        ua[element[1].text] = dict(
            desc = element[2].text,
            type = _parse_type(element[3].text),
            comment = element[4].text,
            link = (element[5].text, element[6].text),
        )

    return ua


def _parse_type(text):
    if text is None:    return

    # type_list = list()
    # for letter in text.split():
    #     type_list.append(_TYPE_CODE.get(letter))
    # return tuple(type_list)

    type_list = list()
    text_list = text.split()
    for key in _TYPE_CODE.keys():
        type_list.append(key if (key in text_list) else '-')
    return text if type_list == ['-']*6 else ' '.join(type_list)


if __name__ == '__main__':
    import pprint
    pprint.pprint(parse())
    # import json
    # with open('useragents.json', 'w') as file:
    #     json.dump(parse(), file)
