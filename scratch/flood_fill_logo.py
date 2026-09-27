from PIL import Image
import collections

def flood_fill_transparent():
    img = Image.open('static/images/logo.png').convert('RGBA')
    w, h = img.size
    pixels = img.load()

    # We will do BFS flood fill from the 4 outer image corners
    # Any pixel connected to the corner that is dark (brightness < 35) becomes alpha = 0
    visited = set()
    queue = collections.deque([(0, 0), (w-1, 0), (0, h-1), (w-1, h-1),
                               (1, 1), (w-2, 1), (1, h-2), (w-2, h-2)])

    for pt in queue:
        visited.add(pt)

    def is_dark(x, y):
        r, g, b, a = pixels[x, y]
        # Brightness threshold for black background
        return (r * 0.299 + g * 0.587 + b * 0.114) < 35

    while queue:
        cx, cy = queue.popleft()
        if is_dark(cx, cy):
            pixels[cx, cy] = (0, 0, 0, 0)
            
            # Check 4 neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    if is_dark(nx, ny):
                        queue.append((nx, ny))

    img.save('static/images/logo.png', 'PNG')
    img.save('static/images/new_logo.png', 'PNG')
    print("Exact flood-fill transparent mask applied to static/images/logo.png!")

if __name__ == '__main__':
    flood_fill_transparent()
