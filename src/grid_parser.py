import re
import requests

def _convert_to_export_url(doc_url: str) -> str:
    """
    Convert a standard Google Doc URL to a plain-text export URL.
    Example:
      https://docs.google.com/document/d/<DOC_ID>/edit
    => https://docs.google.com/document/d/<DOC_ID>/export?format=txt
    """
    match = re.search(r"/d/([\w-]+)", doc_url)
    if not match:
        raise ValueError(f"Invalid Google Doc URL: {doc_url}")
    doc_id = match.group(1)
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

    # 1) Turn the entire document into a flat list of tokens
    tokens = re.split(r"\s+", resp.text.strip())
    # tokens[0:3] == ["x-coordinate","Character","y-coordinate"]
    data = tokens[3:]  # everything after the header

    # sanity check
    if len(data) % 3 != 0:
        print(f"⚠️  Unexpected token count: {len(data)} is not a multiple of 3")
        return

    # 2) Build entries = [(x,y,char), ...]
    entries = []
    for i in range(0, len(data), 3):
        xs, ch, ys = data[i], data[i+1], data[i+2]
        try:
            x, y = int(xs), int(ys)
        except ValueError:
            print(f"⚠️  Couldn’t parse coords: {xs!r}, {ys!r}")
            continue
        entries.append((x, y, ch))

    # 3) Now you have entries!  Proceed as before:
    if not entries:
        print("❌ No entries found!")
        return

    max_x = max(x for x, _, _ in entries)
    max_y = max(y for _, y, _ in entries)
    width, height = max_x + 1, max_y + 1

    # 4) Build and print the grid
    grid = [[" "] * width for _ in range(height)]
    for x, y, ch in entries:
        grid[y][x] = ch

    for row in grid:
        print("".join(row))

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

