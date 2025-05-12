import re
import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


def _convert_to_export_url(doc_url: str) -> str:
    """
    Convert Google Doc URLs into a plain-text export URL.
    Supports both regular edit links (/d/<ID>/) and published links (/d/e/<ID>/pub).
    """
    # 1) Published form: /d/e/<PUB_ID>/pub
    m = re.search(r"/d/e/([-\w]+)/", doc_url)
    if m:
        pub_id = m.group(1)
        return f"https://docs.google.com/document/d/e/{pub_id}/pub?output=txt"

    # 2) Edit form: /d/<DOC_ID>/
    m = re.search(r"/d/([-\w]+)/", doc_url)
    if not m:
        raise ValueError(f"Couldn’t find a document ID in {doc_url!r}")
    doc_id = m.group(1)
    return f"https://docs.google.com/document/d/{doc_id}/export?format=txt"


def print_grid_from_doc(doc_url: str) -> None:
    """
    Fetch, parse, and print a 2D grid of characters from a Google Doc table.

    The Doc is expected to export as plain text with:
      • A header row: "x-coordinate", "Character", "y-coordinate"
      • Then a flat sequence of cells: x, char, y, x, char, y, …

    Parsing steps:
      1) Split entire document on whitespace into tokens.
      2) Discard the first three header tokens.
      3) Every group of 3 tokens thereafter is (x, char, y).
      4) Convert x and y to ints; collect (x, y, char) tuples.
      5) Compute grid width = max_x+1, height = max_y+1.
      6) Fill a 2D array of spaces, then place each char at (x, y).
      7) Print each row joined as a string.

    Time Complexity: O(T + W·H)
      • T = total number of tokens (~3N entries + header)
      • W = width of grid, H = height of grid

    Space Complexity: O(W·H) for the output grid
    """
    # Build export URL and fetch content
    export_url = _convert_to_export_url(doc_url)
    response = requests.get(export_url)
    response.raise_for_status()
    text = response.text

    # 1) Turn the entire document into a flat list of tokens
    tokens = re.split(r"\s+", response.text.strip())
    # tokens[0:3] == ["x-coordinate","Character","y-coordinate"]
    data = tokens[3:]  # everything after the header

    #DEBUG # immediately after data = tokens[3:]
    print(f"Total data tokens = {len(data)}")
    print("First 50 tokens:", data[:50])
    
    # show exactly what your parser is seeing, and why it’s rejecting every triple
    for idx in range(min(20, len(data) - 2)):
        xs, ch, ys = data[idx], data[idx+1], data[idx+2]
        is_x_int = xs.lstrip('-').isdigit()
        is_y_int = ys.lstrip('-').isdigit()
        is_char_single = len(ch) == 1
        print(f"{idx:2d} → xs={xs!r} int?{is_x_int} | ch={ch!r} len?{len(ch)} | ys={ys!r} int?{is_y_int}")


    # 2) Sliding-window parse: int, single-char, int
    entries = []
    i = 0
    N = len(data)
    while i < N - 2:
        xs, ch, ys = data[i], data[i+1], data[i+2]
        if xs.lstrip('-').isdigit() and ys.lstrip('-').isdigit() and len(ch) == 1:
            x, y = int(xs), int(ys)
            entries.append((x, y, ch))
            i += 3
        else:
            i += 1

    # Fallback: HTML table parsing
    if (not entries or len(data) % 3 != 0) and BeautifulSoup:
        soup = BeautifulSoup(text, 'html.parser')
        table = soup.find('table')
        if table:
            cells = table.find_all(['th', 'td'])
            tokens = [cell.get_text(strip=True) for cell in cells]
            data = tokens[3:]
            entries = extract_entries(data)


    # 3) Now you have entries!  Proceed as before:
    if not entries:
        print("❌ No entries found!")
        return

    max_x = max(e[0] for e in entries)
    max_y = max(e[1] for e in entries)
    width, height = max_x + 1, max_y + 1

    # 4) Build and print the grid
    grid = [[" "] * width for _ in range(height)]
    for x, y, ch in entries:
        grid[y][x] = ch

    # Print from top row down to bottom
    for row in range(height - 1, -1, -1):
        print("".join(grid[row]))

def debug_print_grid(doc_url: str):
    export_url = _convert_to_export_url(doc_url)
    print(f"→ Export URL: {export_url}")
    
    resp = requests.get(export_url)
    print(f"→ HTTP status: {resp.status_code}\n")
    
    lines = resp.text.splitlines()
    print(f"→ Raw lines ({len(lines)}): {lines[:10]!r}\n")
    
    entries = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        c, xs, ys = parts
        try:
            x, y = int(xs), int(ys)
            entries.append((x, y, c))
        except ValueError:
            continue
    
    print(f"→ Parsed entries: {len(entries)} (showing up to 10):")
    print(entries[:10], "\n")
    
    if not entries:
        print("❌ No valid char-coordinate entries found.")
        return
    
    max_x = max(x for x,_,_ in entries)
    max_y = max(y for _,y,_ in entries)
    print(f"→ Grid size: {max_y+1} rows × {max_x+1} cols\n")
    
    grid = [[" "] * (max_x+1) for _ in range(max_y+1)]
    for x, y, c in entries:
        grid[y][x] = c
    
    print("→ Final grid:")
    for row in grid:
        print("".join(row))

