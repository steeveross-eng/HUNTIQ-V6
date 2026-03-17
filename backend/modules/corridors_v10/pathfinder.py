"""
CORRIDORS-V10 — Algorithme A* sur grille de couts
=====================================================
Pathfinding a moindre cout entre deux cellules de la grille.
Supporte 8 directions (diagonales incluses).
Barriere = cout >= INFINITY_COST.
Garantit un chemin optimal si existant.
BCE-4X: Aucun corridor hors grille. Pas de self-intersection.
"""
import heapq
import math

INFINITY_COST = 999999.0
SQRT2 = math.sqrt(2)

# 8 directions: N, NE, E, SE, S, SW, W, NW
DIRECTIONS = [
    (-1, 0, 1.0),    # N
    (-1, 1, SQRT2),  # NE
    (0, 1, 1.0),     # E
    (1, 1, SQRT2),   # SE
    (1, 0, 1.0),     # S
    (1, -1, SQRT2),  # SW
    (0, -1, 1.0),    # W
    (-1, -1, SQRT2), # NW
]


def _heuristic(r1: int, c1: int, r2: int, c2: int) -> float:
    """Distance octile (heuristique admissible pour 8 directions)."""
    dr = abs(r1 - r2)
    dc = abs(c1 - c2)
    return max(dr, dc) + (SQRT2 - 1) * min(dr, dc)


def astar(
    cost_grid: list,
    start: tuple,
    goal: tuple,
    n: int,
    style: str = "lineaire",
) -> dict:
    """
    A* pathfinding sur la grille de couts.

    Args:
        cost_grid: Grille 2D de couts [row][col]
        start: (row, col) depart
        goal: (row, col) destination
        n: Taille de la grille (NxN)
        style: Style de deplacement (affecte le cout diagonal)

    Returns:
        {path: [(row,col),...], cost: float, found: bool, visited: int}
    """
    sr, sc = start
    gr, gc = goal

    # Validation: start et goal dans la grille
    if not (0 <= sr < n and 0 <= sc < n and 0 <= gr < n and 0 <= gc < n):
        return {"path": [], "cost": 0, "found": False, "visited": 0, "reason": "HORS_GRILLE"}

    # Validation: start et goal pas sur barriere
    if cost_grid[sr][sc] >= INFINITY_COST:
        return {"path": [], "cost": 0, "found": False, "visited": 0, "reason": "DEPART_BARRIERE"}
    if cost_grid[gr][gc] >= INFINITY_COST:
        return {"path": [], "cost": 0, "found": False, "visited": 0, "reason": "ARRIVEE_BARRIERE"}

    # Multiplicateur style de deplacement
    style_mults = {
        "lineaire": {"diag": 1.2, "straight": 0.9},     # Prefere lignes droites
        "sinueux": {"diag": 0.95, "straight": 1.0},      # Prefere diagonales/courbes
        "opportuniste": {"diag": 1.0, "straight": 1.0},  # Neutre
        "migratoire": {"diag": 1.1, "straight": 0.85},   # Forte preference droite
        "territorial": {"diag": 1.0, "straight": 1.05},  # Legere preference courbe
    }
    sm = style_mults.get(style, style_mults["opportuniste"])

    # Priority queue: (f_cost, counter, row, col)
    counter = 0
    open_set = [(0 + _heuristic(sr, sc, gr, gc), counter, sr, sc)]
    came_from = {}
    g_score = {(sr, sc): 0.0}
    visited = set()

    while open_set:
        _, _, cr, cc = heapq.heappop(open_set)

        if (cr, cc) in visited:
            continue
        visited.add((cr, cc))

        if cr == gr and cc == gc:
            # Reconstruire le chemin
            path = [(gr, gc)]
            node = (gr, gc)
            while node in came_from:
                node = came_from[node]
                path.append(node)
            path.reverse()
            return {
                "path": path,
                "cost": round(g_score[(gr, gc)], 3),
                "found": True,
                "visited": len(visited),
                "reason": None,
            }

        for dr, dc, base_dist in DIRECTIONS:
            nr, nc = cr + dr, cc + dc
            if not (0 <= nr < n and 0 <= nc < n):
                continue
            if (nr, nc) in visited:
                continue
            if cost_grid[nr][nc] >= INFINITY_COST:
                continue

            # Cout de mouvement
            is_diag = (dr != 0 and dc != 0)
            style_mult = sm["diag"] if is_diag else sm["straight"]
            move_cost = base_dist * cost_grid[nr][nc] * style_mult

            tentative = g_score[(cr, cc)] + move_cost

            if tentative < g_score.get((nr, nc), float("inf")):
                g_score[(nr, nc)] = tentative
                came_from[(nr, nc)] = (cr, cc)
                f = tentative + _heuristic(nr, nc, gr, gc)
                counter += 1
                heapq.heappush(open_set, (f, counter, nr, nc))

    return {
        "path": [],
        "cost": 0,
        "found": False,
        "visited": len(visited),
        "reason": "AUCUN_CHEMIN",
    }


def find_nearest_traversable(cost_grid: list, target: tuple, n: int, max_radius: int = 10) -> tuple:
    """
    Trouve la cellule traversable la plus proche de target.
    Utilise une recherche BFS en spirale.
    """
    tr, tc = target
    if 0 <= tr < n and 0 <= tc < n and cost_grid[tr][tc] < INFINITY_COST:
        return target

    for radius in range(1, max_radius + 1):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if abs(dr) != radius and abs(dc) != radius:
                    continue
                nr, nc = tr + dr, tc + dc
                if 0 <= nr < n and 0 <= nc < n and cost_grid[nr][nc] < INFINITY_COST:
                    return (nr, nc)

    return None
