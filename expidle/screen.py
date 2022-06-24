import pyautogui
import math

def show_entire_screen():
  pyautogui.screenshot().show()

def capture_window_named(name):
  windows = pyautogui.getWindowsWithTitle(name)
  assert len(windows) == 1
  w = windows[0]
  # print(w)
  bounds = (w.left, w.top, w.width, w.height)
  # print(dir(w))
  # print(bounds)
  w.activate()
  return pyautogui.screenshot(region=bounds)

def draw_square(cx, cy, r, img):
  pix = img.load()
  left = cx - r
  right = cx + r
  top = cy - r
  bottom =  cy + r
  for x in range(left,right):
    for y in [top, bottom]:
      if x < img.size[0] and y < img.size[1]:
        pix[x,y] = (255,0,0)
  for x in [left, right]:
    for y in range(top, bottom):
      if x < img.size[0] and y < img.size[1]:
        pix[x,y] = (255,0,0)


def draw_squares(img):
  radius = 45
  per_col_offset = [
    math.cos(math.radians(-30)) * radius * 2,
    -math.sin(math.radians(-30)) * radius * 2,
  ]
  per_row_offset = [
    math.cos(math.radians(-150)) * radius * 2,
    -math.sin(math.radians(-150)) * radius * 2,
  ]
  origin = (305, 360)
  for row in range(0,7):
    for col in range(0,7):
      draw_square(origin[0] + int(row * per_row_offset[0]) + int(col * per_col_offset[0]),
                  origin[1] + int(row * per_row_offset[1]) + int(col * per_col_offset[1]),
                  radius, img)
  return img

draw_squares(capture_window_named("BlueStacks")).show()