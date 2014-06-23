from __future__ import absolute_import, print_function, division, unicode_literals
from collections import OrderedDict
import xml.etree.ElementTree as ET
import json
import os

def parse_sprites(_sprites):
    def walk_dir(node, path):
        # walk dirs
        for dir in node.findall('./dir'):
            name = dir.get('name')
            full_path = path + '/' + name
            if path == '/':
                full_path = full_path[1:]
            for x in walk_dir(dir, full_path):
                yield x

        # walk sprites in this dir
        node_name = node.get('name')
        for spr in node.findall('./spr'):
            name = spr.get('name')
            full_path = path + '/' + name
            if path == '/':
                full_path = full_path[1:]
            print('Found frame',full_path)

            x = int(spr.get('x'))
            y = int(spr.get('y'))
            w = int(spr.get('w'))
            h = int(spr.get('h'))

            # always refer to image 0
            # x/y offset, default to 0
            frame_name = '{}_{}'.format(node_name, name)

            frame = OrderedDict([
                ('frame', OrderedDict([('x', x), ('y', y), ('w', w), ('h', h)])),
                ('rotated', False),
                ('trimmed', False),
                ('spriteSourceSize', OrderedDict([('x', x), ('y', y), ('w', w), ('h', h)])),
                ('sourceSize', OrderedDict([('w', w), ('h', h)])),
            ])

            yield frame_name, frame

    # parse the sprites and generate a list of frames
    # make a list and a dict with name:index pairs for referencing
    frames = OrderedDict()

    # recurse down the path
    definitions = _sprites.find('definitions')
    root = definitions.find('./')
    for name, frame in walk_dir(root, '/'):
        frames[name] = frame

    return frames

def parse(sprites):
    frames = parse_sprites(sprites)

    image = sprites.get('name')
    data = {
        'frames': frames,
        'meta': {
            'app': 'https://github.com/adamlwgriffiths/dfe_to_tp_pixi',
            #'version': '1.0',
            'image': image,
            #'format': 'RGBA8888',
            #'size': {'w':,'h':,},
            'scale': '1',
        }
    }

    # return json
    return data

def load_files(sprites_path):
    with open(sprites_path, 'r') as f:
        sprites = f.read()
    sprites_xml = ET.fromstring(sprites)

    return sprites_xml

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert darkFunction Editor animations to TexturePacker / Easel json blobs")
    parser.add_argument("sprite", help="The darkFunction Editor .sprite file")
    parser.add_argument("output", help="The json file to save to")
    args = parser.parse_args()

    sprite = os.path.abspath(args.sprite)
    sprites_xml = load_files(sprite)
    result = parse(sprites_xml)

    output = os.path.abspath(args.output)
    with open(args.output, 'w') as f:
        f.write(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))


if __name__ == '__main__':
    main()
