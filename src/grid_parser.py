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
    Fetch, parse, and print a 2D grid of characters from a Google Doc.

    Each line in the document is expected to contain exactly three
    whitespace-separated fields: <character> <x> <y>.

    Characters are placed at (x, y) in the grid (0-indexed),
    with missing positions filled by spaces.

    Time Complexity: O(N + W*H) where N = number of entries,
    W = max x + 1, H = max y + 1
    Space Complexity: O(W*H)
    """
    # Build export URL and fetch content
    export_url = _convert_to_export_url(doc_url)
    response = requests.get(export_url)
    response.raise_for_status()

    # Parse lines
    entries = []
    max_x = max_y = 0
    for line in response.text.splitlines():
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        char, xs, ys = parts
        try:
            x = int(xs)
            y = int(ys)
        except ValueError:
            continue
        entries.append((x, y, char))
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    # Initialize grid of spaces
    width = max_x + 1
    height = max_y + 1
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Place characters
    for x, y, char in entries:
        grid[y][x] = char

    # Print rows
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

