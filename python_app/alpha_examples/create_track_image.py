"""
    Simple helper script that takes the txt file produced by 'track_discovery_example' combine the thumbs
    of the pieces together in a single image. It's just a quick 10 minutes script and it
    won't work generally, but it should get you started if you'd like to explore track mapping more.
    Images are stored in the 'track_images' folder and come from here
    https://github.com/tiker/AnkiNodeDrive/tree/master/images.

    Thanks to https://gist.github.com/glombard/7cd166e311992a828675 for getting us started.


    ATTENTION: please note that this script has different dependencies than the general sdk.

    # Combine multiple images into one.
    #
    # To install the Pillow module on Mac OS X:
    #
    # $ xcode-select --install
    # $ brew install libtiff libjpeg webp little-cms2
    # $ pip install Pillow
"""
from PIL import Image


THUMB_SIZE = 256  # image of the thumb-sized pieces
FINAL_IMAGE_SIZE = 1200  # final size image - should be probably be cropped at the end...
TRACK_FILE = 'track_piece_list.txt'  # input file
PIECE_TYPE = {
                 '34': ('straight', 'EAST'),  # mapping track id with type and "direction"
                 '36': ('straight', 'WEST'),  # direction could vary with track orientation but this
                 '39': ('straight', 'EAST'),  # will work for our sample oval track
                 '57': ('straight', 'WEST'),
                 '17': ('turn', 'SOUTH'),
                 '18': ('turn', 'WEST'),
                 '20': ('turn', 'NORTH'),
                 '23': ('turn', 'EAST'),
              }


def get_next_coors(last_piece_type, last_x, last_y, size):
    if last_piece_type[1] == "EAST":
        return last_x + size, last_y
    elif last_piece_type[1] == "WEST":
        return last_x - size, last_y
    elif last_piece_type[1] == "SOUTH":
        return last_x, last_y + size
    elif last_piece_type[1] == "NORTH":
        return last_x, last_y - size
    else:
        raise Exception('Type not allowed {}'.format(last_piece_type))


def main():
    with open(TRACK_FILE, 'r') as track_file:
        pieces = [l.strip() for l in track_file]
    print('{} pieces found in the track!'.format(len(pieces)))

    # start calculating x/y for the thumbs
    thumbs_coors = []
    # the first one is always the start piece n. 34 and it starts in the middle of w/h
    assert(pieces[0] == '34')
    current_x = int(FINAL_IMAGE_SIZE / 2)
    current_y = int(FINAL_IMAGE_SIZE / 2)
    thumbs_coors.append({
        'id': pieces[0],
        'coors': (current_x, current_y)
    })
    next_x, next_y = get_next_coors(PIECE_TYPE[thumbs_coors[-1]['id']], current_x, current_y, THUMB_SIZE)
    # loop over other pieces and calculate position with some hacks
    for idx, piece_id in enumerate(pieces[1:]):
        current_x = next_x
        current_y = next_y
        thumbs_coors.append({
            'id': piece_id,
            'coors': (current_x, current_y)
        })
        next_x, next_y = get_next_coors(PIECE_TYPE[thumbs_coors[-1]['id']], current_x, current_y, THUMB_SIZE)

    # finally compose the image
    track_image = Image.new("RGB", (FINAL_IMAGE_SIZE, FINAL_IMAGE_SIZE))
    for t in thumbs_coors:
      img = Image.open('track_images/{}.png'.format(t['id']))
      img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.ANTIALIAS)
      track_image.paste(img, (t['coors'][0], t['coors'][1]))

    track_image.save('track_image.jpg')

    print('All done, see you, space cowboys!')

    return


if __name__ == '__main__':
    main()
