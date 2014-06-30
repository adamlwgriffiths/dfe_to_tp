from __future__ import absolute_import, print_function, division, unicode_literals
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

            frame = {
                'frame': {'x': x, 'y': y, 'w': w, 'h': h},
                'rotated': False,
                'trimmed': False,
                'spriteSourceSize': {'x': x, 'y': y, 'w': w, 'h': h},
                'sourceSize': {'w': w, 'h': h},
            }

            yield full_path, frame

    # parse the sprites and generate a list of frames
    # make a list and a dict with name:index pairs for referencing
    frames = []
    frame_lookup = {}

    # recurse down the path
    definitions = _sprites.find('definitions')
    root = definitions.find('./')
    for path, frame in walk_dir(root, '/'):
        frame_lookup[path] = len(frames)
        frames.append(frame)

    return frames, frame_lookup

def parse_anims(_frames, frame_lookup, _anim):
    def walk_anims():
        for anim in _anim.findall('./anim'):
            name = anim.get('name')
            frames = []
            print('Processing',name)
            for cell in anim.findall('./cell'):
                #speed += int(cell.get('delay'))

                # get the first sprite ignore the others
                spr = cell.find('./spr')
                x_offset = int(spr.get('x'))
                y_offset = int(spr.get('y'))

                sprite_name = spr.get('name')
                # find the sprite in our sprites list
                frame = _frames[frame_lookup[sprite_name]]
                frame = frame.copy()
                frames.append(frame)

                #print(sprite_name)
                #print(frame)
                #print(_frames)
                # update the x/y offset
                #_frame = _frames[sprite_name]
                frame['trimmed'] = True
                if x_offset < 0:
                    frame['spriteSourceSize']['x'] -= abs(x_offset)
                else:
                    frame['spriteSourceSize']['w'] += abs(x_offset)
                if y_offset < 0:
                    frame['spriteSourceSize']['y'] -= abs(y_offset)
                else:
                    frame['spriteSourceSize']['h'] += abs(y_offset)
                frame['spriteSourceSize']['w'] = frame['spriteSourceSize']['w']
                frame['spriteSourceSize']['h'] = frame['spriteSourceSize']['h']

            yield name, frames

    anims = {}
    for name, frames in walk_anims():
        for index, frame in enumerate(frames):
            frame_name = '{}{}'.format(name,index)
            anims[frame_name] = frame

    return anims

def parse(sprites, anim, framerate=20):
    frames, frame_lookup = parse_sprites(sprites)
    animations = parse_anims(frames, frame_lookup, anim)

    image = sprites.get('name')
    w = sprites.get('w')
    h = sprites.get('h')
    data = {
        'frames': animations,
        'meta': {
            'app': 'https://github.com/adamlwgriffiths/dfe_to_tp',
            #'version': '1.0',
            'image': image,
            #'format': 'RGBA8888',
            'size': {'w':w,'h':h},
            'scale': '1',
        }
    }

    # return json
    return data

def load_files(anim_path):
    with open(anim_path, 'r') as f:
        anim = f.read()
    anim_xml = ET.fromstring(anim)

    # get the sprite sheet
    spritesheet = anim_xml.get('spriteSheet')
    sprites_path = os.path.join(os.path.dirname(anim_path), spritesheet)
    with open(sprites_path, 'r') as f:
        sprites = f.read()
    sprites_xml = ET.fromstring(sprites)

    return sprites_xml, anim_xml

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert darkFunction Editor animations to TexturePacker / Easel json blobs")
    parser.add_argument("anim", help="The darkFunction Editor .anim file")
    parser.add_argument("output", help="The json file to save to")
    parser.add_argument("-f", "--framerate", default=20, type=int, help="The framerate to use")
    args = parser.parse_args()

    anim = os.path.abspath(args.anim)
    sprites_xml, anim_xml = load_files(anim)
    result = parse(sprites_xml, anim_xml, args.framerate)

    output = os.path.abspath(args.output)
    with open(args.output, 'w') as f:
        f.write(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))


if __name__ == '__main__':
    main()
