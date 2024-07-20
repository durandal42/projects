import cv2 as cv
import numpy as np
# import collections

import pq

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

    if gem_names != most_recent_gem_names:
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


# cribbed from https://fossies.org/linux/opencv/samples/python/hist.py
bins = np.arange(256).reshape(256, 1)


def hist_curve_image(hists):
  # cribbed from https://fossies.org/linux/opencv/samples/python/hist.py
  h = np.zeros((300, 256, 3))
  colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
  for col, hist in zip(colors, hists):
    pts = np.int32(np.column_stack((bins, hist)))
    cv.polylines(h, [pts], False, col)
    y = np.flipud(h)
  return y


def hist_curves(im, mask=None):
  result = []
  for ch in range(3):
    hist = cv.calcHist([im], [ch], mask, [256], [0, 256])
    cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)
    result.append(hist)
  return result


SPRITE_NAMES = [
    "mana_green", "mana_red", "mana_yellow", "mana_blue",
    "skull", "purple_star", "gold_coin", "big_skull",
]
GEM_SPRITES = [
    cv.imread(f"sprites/{name}.png") for name in SPRITE_NAMES
]


PLAY_X_BEGIN, PLAY_Y_BEGIN = 499, 122
PLAY_X_LIMIT, PLAY_Y_LIMIT = 1419, 1042
PLAY_GRID_SCALE = 115

GEM_HISTS = [hist_curves(im[PLAY_GRID_SCALE//3:
                            - PLAY_GRID_SCALE//3,
                            PLAY_GRID_SCALE//3:
                            - PLAY_GRID_SCALE//3]) for im in GEM_SPRITES]


def inspect(img):
  # TODO(durandal): if the play area isn't ringed by a white border, it's not our turn!

  # histogram play pieces
  hists = get_grid_hists(img)

  gem_names = identify_gems(hists)
  save_unknown_sprites(gem_names, img)

  # inspection debug visualizations:
  # render_hists(hists, img)
  # render_hist_similarity_grid(hists, img)

  return gem_names


def render_reference_grid(img):
  # reference grid - whole screen
  for x in range(0, FRAME_WIDTH, 100):
    cv.line(img, (x, 0), (x, FRAME_HEIGHT), COLOR_GRAY, 1)
  for y in range(0, FRAME_HEIGHT, 100):
    cv.line(img, (0, y), (FRAME_WIDTH, y), COLOR_GRAY, 1)


def match_target(img, x_begin, y_begin, x_limit, y_limit):
  # only match on inner 9th of the sprite, to avoid borders and reticles.
  return img[y_begin + PLAY_GRID_SCALE//3:
             y_limit - PLAY_GRID_SCALE//3,
             x_begin + PLAY_GRID_SCALE//3:
             x_limit - PLAY_GRID_SCALE//3]


def enumerate_grid(x_origin=PLAY_X_BEGIN, y_origin=PLAY_Y_BEGIN,
                   grid_scale=PLAY_GRID_SCALE):
  for r in range(8):
    y_begin = y_origin + r*grid_scale
    y_limit = y_begin + grid_scale
    for c in range(8):
      x_begin = x_origin + c*grid_scale
      x_limit = x_begin + grid_scale
      yield r, c, x_begin, y_begin, x_limit, y_limit


def get_grid_hists(img):
  hists = {}
  for r, c, x_begin, y_begin, x_limit, y_limit in enumerate_grid():
    # only match on inner 9th of the sprite, to avoid borders and reticles.
    hist = hist_curves(
        match_target(img, x_begin, y_begin, x_limit, y_limit))
    hists[(r, c)] = hist
  return hists


unknown_sprites = 0


def identify_gems(hists):
  result = {}
  for coords, hist in hists.items():
    for i, known_hist in enumerate(GEM_HISTS):
      if compare_rbg_hists(hist, known_hist) > 0.5:
        result[coords] = SPRITE_NAMES[i]
        break
    else:
      global unknown_sprites
      new_name = f"unknown_{unknown_sprites}"
      result[coords] = new_name
      GEM_HISTS.append(hist)
      SPRITE_NAMES.append(new_name)
      # print("encountered unknown sprite!")
      unknown_sprites += 1
  return result


saved_unknown_sprites = set()
UNKNOWN_SPRITE_SAVE_LIMIT = 10


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
    cv.imwrite(f"{gem_name}.png",
               img[y_begin:y_limit, x_begin:x_limit, :])
    saved_unknown_sprites.add(gem_name)


def render_gem_identities(img, gems):
  for r, c, x_begin, y_begin, x_limit, y_limit in enumerate_grid():
    gem_name = gems[(r, c)]
    cv.putText(img=img, text=gem_name,
               org=(x_begin, (y_begin + y_limit)//2),
               fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
               color=COLOR_WHITE,
               thickness=2, lineType=cv.LINE_AA)


def render_hists(hists, img):
  for r, c, x_begin, y_begin, x_limit, y_limit in enumerate_grid():
    hist = hists[(r, c)]
    hist_img = hist_curve_image(hist)
    hist_img = cv.resize(hist_img, (PLAY_GRID_SCALE, PLAY_GRID_SCALE))
    img[y_begin:y_limit, x_begin:x_limit, :] = hist_img


def render_hist_similarity_grid(hists, img):
  for r1, c1, x1_begin, y1_begin, x1_limit, y1_limit in enumerate_grid():
    for r2, c2, x2_begin, y2_begin, x2_limit, y2_limit in enumerate_grid(
            x1_begin, y1_begin, PLAY_GRID_SCALE//8):

      value = int(compare_rbg_hists(
          hists[(r1, c1)], hists[(r2, c2)]) * 256)
      color = (value, value, value)

      cv.rectangle(img,
                   (x2_begin, y2_begin),
                   (x2_limit, y2_limit),
                   color, -1)


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
  # render_reference_grid(img)
  # render_play_grid(img)
  # render_gem_identities(img, gem_names)

  if not analysis:
    return

  moves_and_yields, chosen_move = analysis
  render_moves_and_yields(moves_and_yields, img, chosen=chosen_move)


def compare_rbg_hists(hists1, hists2):
  similarity = 1.0
  for h1, h2 in zip(hists1, hists2):
    similarity *= cv.compareHist(h1, h2, 0)
  return similarity


SPRITE_NAME_TO_SOLVER_GEM_NAME = {
    "mana_green": "GREEN",
    "mana_red": "RED",
    "mana_yellow": "YELLOW",
    "mana_blue": "BLUE",
    "skull": "SKULL",
    "purple_star": "STAR",
    "gold_coin": "COIN",
    "big_skull": "SKULL",  # TODO(durandal): support big skulls in solver
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

  return moves_and_yields, chosen_move


dragging = False


def mouse_listener(event, x, y, flags, param):
  global dragging
  if event == cv.EVENT_MOUSEMOVE:
    return
  if event == cv.EVENT_LBUTTONDOWN:
    print(f"mouse down at {x},{y}")
    dragging = True
  elif event == cv.EVENT_LBUTTONUP:
    print(f"mouse up at {x},{y}")
    dragging = False
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
