from picross import solve_grid

# $ pip install requests
from requests_html import HTMLSession

# $ pip install beautifulsoup4
from bs4 import BeautifulSoup

import time


def get_nonogram_table(url):
  fetch_start = time.time()

  session = HTMLSession()
  print("grabbing html...")
  r = session.get(url)
  # print(r.content)

  fetch_end = time.time()
  print(f"fetched table in {fetch_end - fetch_start:.2f} seconds from {url}")

  print("rendering html...")
  r.html.render()
  render_end = time.time()
  print(f"rendered html+javascript in {render_end - fetch_end:.2f} seconds")

  print("soupifying...")
  soup = BeautifulSoup(r.html.raw_html, 'html.parser')
  table = soup.find_all(id='nonogram_table')[0]
  # print(table)
  soup_end = time.time()
  print(f"found table within rendered page in {soup_end - render_end:.2f} seconds")

  return table


def extract_runs(nonogram_table):
  # print("finding column runs...")
  nmtt = nonogram_table.find_all(class_="nmtt")[0]
  nmtt_rows = nmtt.find_all("tr")
  column_runs_transposed = []
  for row in nmtt_rows:
    cells = row.find_all("td")
    # print("new row:")
    row_values = []
    for c in cells:
      v = c.find_all("div")[0].contents[0].strip()
      if v:
        v = int(v)
      # print(v, "", end='')
      row_values.append(v)
    # print(row_values)
    column_runs_transposed.append(row_values)

  column_runs = []
  for i in range(len(column_runs_transposed[0])):
    column_runs.append([v[i] for v in column_runs_transposed if v[i]])
  # print(column_runs)

  # print("finding row runs...")
  nmtl = nonogram_table.find_all(class_="nmtl")[0]
  nmtl_rows = nmtl.find_all("tr")
  row_runs = []
  for row in nmtl_rows:
    cells = row.find_all("td")
    # print("new row:")
    row_values = []
    for c in cells:
      v = c.find_all("div")[0].contents[0].strip()
      if v:
        row_values.append(int(v))
      # print(v, "", end='')
    # print(row_values)
    row_runs.append(row_values)

  # print(row_runs)

  return column_runs, row_runs


def fetch_nonograms_org_by_idx(idx):
  return extract_runs(get_nonogram_table(
      "https://www.nonograms.org/nonograms/i/%d" % idx))

# solve_nonograms_org_by_idx(2162)
# solve_nonograms_org_by_idx(21072)

if __name__ == "__main__":
  idx = 21072

  import sys
  # print(sys.argv)
  if len(sys.argv) > 1:
    idx = int(sys.argv[1])

  col_runs, row_runs = fetch_nonograms_org_by_idx(idx)
  solve_grid(col_runs, row_runs)
  print(f"solved nonograms.org puzzle #{idx}.")

# TODO(durandal): cache html lookups by idx
