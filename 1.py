def research_universe(matrix, key):
    rows = len(matrix)
    cols = len(matrix[0])
    result = [[0] * cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue

                    nr = (r + dr) % rows
                    nc = (c + dc) % cols

                    if key(matrix[nr][nc]):
                        count += 1
            result[r][c] = count

    return result
