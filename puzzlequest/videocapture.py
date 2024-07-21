import pq
import cv2 as cv
import numpy as np

from pytesseract import pytesseract
# needs: https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# import collections


FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (127, 127, 127)
COLOR_GREEN = (0, 255, 0)


def open_stream():
  print("Opening video capture stream...")
  cap = cv.VideoCapture(1)
  print("Frame default resolution: "
        f"({int(cap.get(cv.CAP_PROP_FRAME_WIDTH))} x "
        f"{int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))})")
  print("Setting video capture resolution to 1080p...")
  cap.set(cv.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
  cap.set(cv.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
  print(f"Frame resolution set to: "
        f"({int(cap.get(cv.CAP_PROP_FRAME_WIDTH))} x "
        f"{int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))})")

  if not cap.isOpened():
    print("Cannot open camera; exiting.")
    exit()

  return cap


def loop(cap):
  most_recent_gem_names = None
  most_recent_analysis = None
  while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
      print("Can't receive frame (stream end?). Exiting...")
      break

    # Our operations on the frame come here
    gem_names = inspect(frame)

    if gem_names is None:
      most_recent_gem_names = None
      most_recent_analysis = None
    elif gem_names != most_recent_gem_names:
      most_recent_gem_names = gem_names
      most_recent_analysis = analyze(gem_names)

    # TODO(durandal): plug into the solver
    if not dragging:
      decorate(frame, most_recent_gem_names, most_recent_analysis)

    # Display the resulting frame
    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
      break


def cleanup(cap):
  # When everything done, release the capture
  cap.release()
  cv.destroyAllWindows()


SPRITE_NAMES = [
    "mana_green", "mana_red", "mana_yellow", "mana_blue",
    "skull", "purple_star", "gold_coin", "big_skull",
    "wild2", "wild3", "wild6"
]
GEM_SPRITES = [
    cv.imread(f"sprites/{name}.png") for name in SPRITE_NAMES
]
# for name, sprite in zip(SPRITE_NAMES, GEM_SPRITES):
#   print(f"loaded sprite with name {name} and size {sprite.shape}")

PLAY_X_BEGIN, PLAY_Y_BEGIN = 499, 122
PLAY_X_LIMIT, PLAY_Y_LIMIT = 1419, 1042
PLAY_GRID_SCALE = 115


def inspect(img):
  # TODO(durandal): if the play area isn't ringed
  # by a white border, it's not our turn!
  turn_test_pixel = img[1047, 512]
  # print("turn_test_pixel:", turn_test_pixel)
  if min(turn_test_pixel) < 127:
    # print("bailing out of inspect() because it's not our turn!")
    return None

  sprites = get_grid_sprites(img)

  gem_names, gem_probs = identify_gems(sprites)
  if not gem_names:
    return

  save_unknown_sprites(gem_names, img)

  # inspection debug visualizations:
  # render_reference_grid(img)
  # render_play_grid(img)
  render_gem_identities(img, gem_names, gem_probs)

  return gem_names


def render_reference_grid(img):
  # reference grid - whole screen
  for x in range(0, FRAME_WIDTH, 100):
    cv.line(img, (x, 0), (x, FRAME_HEIGHT), COLOR_GRAY, 1)
  for y in range(0, FRAME_HEIGHT, 100):
    cv.line(img, (0, y), (FRAME_WIDTH, y), COLOR_GRAY, 1)


def match_target(img, x_begin=0, y_begin=0, x_limit=None, y_limit=None):
  # print("getting match target for image of shape", img.shape)
  if x_limit is None:
    x_limit = img.shape[0]
  if y_limit is None:
    y_limit = img.shape[1]
  # only match on inner 9th of the sprite, to avoid borders and reticles.
  result = img[y_begin + PLAY_GRID_SCALE//3:
               y_limit - PLAY_GRID_SCALE//3,
               x_begin + PLAY_GRID_SCALE//3:
               x_limit - PLAY_GRID_SCALE//3]
  # print("result has shape", result.shape)
  return result


def enumerate_grid(x_origin=PLAY_X_BEGIN, y_origin=PLAY_Y_BEGIN,
                   grid_scale=PLAY_GRID_SCALE):
  for r in range(8):
    y_begin = y_origin + r*grid_scale
    y_limit = y_begin + grid_scale
    for c in range(8):
      x_begin = x_origin + c*grid_scale
      x_limit = x_begin + grid_scale
      yield r, c, x_begin, y_begin, x_limit, y_limit


def get_grid_sprites(img):
  sprites = {}
  for r, c, x_begin, y_begin, x_limit, y_limit in enumerate_grid():
    sprite = img[y_begin:y_limit, x_begin:x_limit]
    if (dragging
        and mouse_x in range(x_begin, x_limit)
        and mouse_y in range(y_begin, y_limit)
        ):
      cv.imwrite(f"{r}x{c}.png", sprite)
    sprites[(r, c)] = sprite
  return sprites


unknown_sprites = 0


def match_image(needle, haystack):
  match = cv.matchTemplate(
      needle, haystack, cv.TM_CCOEFF_NORMED)
  return np.max(match)
  # return (256 - np.mean((needle.flatten() - haystack.flatten())**2)) / 256


def identify_gems(sprites):
  gem_names = {}
  gem_probs = {}
  for coords, sprite in sprites.items():
    probs = []
    for template_sprite_name, template_sprite in zip(
            SPRITE_NAMES, GEM_SPRITES):
      probs.append(
          (match_image(match_target(sprite),
                       match_target(template_sprite)),
           template_sprite_name))
    max_prob, max_name = max(probs)
    gem_probs[coords] = max_prob
    if max_prob > 0.5:
      gem_names[coords] = max_name
    else:
      global unknown_sprites
      cv.imshow('debug', sprite)
      new_name = f"unknown_{unknown_sprites}"
      gem_names[coords] = new_name
      GEM_SPRITES.append(sprite)
      SPRITE_NAMES.append(new_name)
      # print("encountered unknown sprite!")
      unknown_sprites += 1
  return gem_names, gem_probs


saved_unknown_sprites = set()
UNKNOWN_SPRITE_SAVE_LIMIT = 100


def save_unknown_sprites(gem_names, img):
  global saved_unknown_sprites
  for r, c, x_begin, y_begin, x_limit, y_limit in enumerate_grid():
    if len(saved_unknown_sprites) >= UNKNOWN_SPRITE_SAVE_LIMIT:
      break
    gem_name = gem_names[(r, c)]
    if gem_name in saved_unknown_sprites:
      continue
    if not gem_name.startswith("unknown"):
      continue
    cv.imwrite(f"unknown_sprites/{gem_name}.png",
               img[y_begin:y_limit, x_begin:x_limit, :])
    saved_unknown_sprites.add(gem_name)


def render_gem_identities(img, gems, probs):
  if not gems:
    return
  for r, c, x_begin, y_begin, x_limit, y_limit in enumerate_grid():
    gem_name = gems[(r, c)]
    cv.putText(img=img, text=gem_name,
               org=(x_begin, (y_begin + y_limit)//2),
               fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
               color=COLOR_WHITE,
               thickness=2, lineType=cv.LINE_AA)
    gem_prob = "%.2f" % probs[(r, c)]
    cv.putText(img=img, text=gem_prob,
               org=(x_begin + 50, (y_begin + y_limit)//2 + 50),
               fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
               color=COLOR_WHITE,
               thickness=2, lineType=cv.LINE_AA)


def render_play_grid(img):
  # play area
  cv.rectangle(img,
               (PLAY_X_BEGIN, PLAY_Y_BEGIN),
               (PLAY_X_LIMIT, PLAY_Y_LIMIT),
               COLOR_GREEN, 2)

  # grid lines
  for x in range(PLAY_X_BEGIN, PLAY_X_LIMIT, PLAY_GRID_SCALE):
    cv.line(img, (x, PLAY_Y_BEGIN), (x, PLAY_Y_LIMIT),
            COLOR_GREEN, 1)
  for y in range(PLAY_Y_BEGIN, PLAY_Y_LIMIT, PLAY_GRID_SCALE):
    cv.line(img, (PLAY_X_BEGIN, y), (PLAY_X_LIMIT, y),
            COLOR_GREEN, 1)


def render_moves_and_yields(moves_and_yields, img, chosen=None):
  for move, yields in moves_and_yields.items():
    assert move[0] == pq.Move.SWAP
    swap_direction = move[1]
    swap_origin = move[2]

    src_r, src_c = swap_origin
    if swap_direction == pq.Swap.VERTICAL:
      dst_r, dst_c = src_r + 1, src_c
    elif swap_direction == pq.Swap.HORIZONTAL:
      dst_r, dst_c = src_r, src_c + 1
    else:
      assert False

    render_center_x = int((src_c+dst_c)/2 * PLAY_GRID_SCALE +
                          PLAY_X_BEGIN + PLAY_GRID_SCALE/2)
    render_center_y = int((src_r+dst_r)/2 * PLAY_GRID_SCALE +
                          PLAY_Y_BEGIN + PLAY_GRID_SCALE/2)
    color = COLOR_WHITE
    if move == chosen:
      color = COLOR_GREEN
    cv.rectangle(img,
                 (render_center_x-5, render_center_y-5),
                 (render_center_x+5, render_center_y+5),
                 color, -1)


def decorate(img, gem_names, analysis):
  if not analysis:
    return

  moves_and_yields, chosen_move = analysis
  render_moves_and_yields(moves_and_yields, img, chosen=chosen_move)


SPRITE_NAME_TO_SOLVER_GEM_NAME = {
    "mana_green": "GREEN",
    "mana_red": "RED",
    "mana_yellow": "YELLOW",
    "mana_blue": "BLUE",
    "skull": "SKULL",
    "purple_star": "STAR",
    "gold_coin": "COIN",
    "big_skull": "BIG_SKULL",
    "wild2": "WILD2",
    "wild3": "WILD3",
    "wild4": "WILD4",
    "wild5": "WILD5",
    "wild6": "WILD6",
}


def analyze(gem_names):
  print("analyze called!")
  grid = []
  for r in range(8):
    grid.append([])
    for c in range(8):
      gem_name = gem_names[(r, c)]
      if gem_name not in SPRITE_NAME_TO_SOLVER_GEM_NAME:
        print(f"Sprite name {gem_name} not found in solver mapping;"
              " cannot proceed with analysis.")
        return None
      solver_gem_name = SPRITE_NAME_TO_SOLVER_GEM_NAME[gem_name]
      grid[r].append(pq.Gem[solver_gem_name])
  board = pq.immutable_board(grid)
  print(pq.pretty_print_board(board))

  moves_and_yields = pq.consider_moves(
      board, cascade=True, permit_spells=False)
  print('available moves (cascade, no spells):',
        pq.pretty_print_dict(moves_and_yields))
  chosen_move = pq.pick_highest_yield(moves_and_yields)
  print('chosen move:', chosen_move)
  print('yields from chosen move:', moves_and_yields[chosen_move][0])
  print('chosen move triggers a free turn:', moves_and_yields[chosen_move][1])

  return moves_and_yields, chosen_move


dragging = False
mouse_x = None
mouse_y = None


def mouse_listener(event, x, y, flags, param):
  global dragging, mouse_x, mouse_y
  if event == cv.EVENT_MOUSEMOVE:
    return
  if event == cv.EVENT_LBUTTONDOWN:
    print(f"mouse down at {x},{y}")
    dragging = True
    mouse_x, mouse_y = x, y
  elif event == cv.EVENT_LBUTTONUP:
    print(f"mouse up at {x},{y}")
    dragging = False
    mouse_x, mouse_y = None, None
    # TODO(durandal): as needed, draw a rect around the dragged area:
    # https://pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/
  else:
    # https://docs.opencv.org/3.4/d0/d90/group__highgui__window__flags.html
    print(event, x, y, flags, param)


def main():
  cap = open_stream()
  cv.namedWindow('frame')
  cv.setMouseCallback('frame', mouse_listener)
  loop(cap)
  cleanup(cap)


if __name__ == '__main__':
  main()
