"""Replace a duplicate part by the part we keep, without moving it in the assembly.

Column-vector convention: a 4x4 matrix T maps local part coordinates to the
parent assembly: x_parent = T @ x_local.

Setup (done once per duplicate pair, in an empty product):
  - leave the duplicate B at the origin (identity),
  - move the part we keep, A, until it lies exactly on top of B.
  D is the placement of A after that move, so  x_B = D @ x_A.

For every instance of B in a parent with placement P (x_parent = P @ x_B),
the kept part A must get placement P' with  P' @ x_A == P @ x_B == P @ D @ x_A:

      P' = P @ D

If you move the duplicate onto the kept part instead, the measured matrix is
inverse(D) and the formula becomes P' = P @ inverse(D_measured).
"""
import numpy as np


def make_matrix(rotation_deg_xyz, translation):
    ax, ay, az = np.radians(rotation_deg_xyz)
    cx, sx, cy, sy, cz, sz = np.cos(ax), np.sin(ax), np.cos(ay), np.sin(ay), np.cos(az), np.sin(az)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    m = np.eye(4)
    m[:3, :3] = rz @ ry @ rx
    m[:3, 3] = translation
    return m


def new_placement(p_duplicate, d_offset):
    """Placement for the kept part so it sits exactly where the duplicate sat."""
    return p_duplicate @ d_offset


def apply(matrix, points):
    homogeneous = np.c_[points, np.ones(len(points))]
    return (matrix @ homogeneous.T).T[:, :3]


def show(name, m):
    print(name)
    for row in m:
        print("  " + "  ".join(f"{v:10.3f}" for v in row))


if __name__ == "__main__":
    np.set_printoptions(suppress=True)
    rng = np.random.default_rng(1)

    # Synthetic "bolt": a handful of points in the kept part's own coordinates.
    part_a = rng.uniform(-10, 10, size=(8, 3))

    # Duplicate B is the same geometry, but its origin sits somewhere else.
    d = make_matrix((0, 0, 90), (12.5, -3.0, 40.0))        # made-up offset
    part_b = apply(d, part_a)                              # so that x_B = D @ x_A

    # --- One example instance, step by step -------------------------------
    p = make_matrix((10, 20, 30), (500.0, 250.0, 80.0))    # duplicate B inside a parent
    p_new = new_placement(p, d)
    print("Example: one instance of the duplicate in a parent assembly\n")
    show("D  (offset, measured once per pair):", d)
    show("P  (placement of the duplicate in the parent):", p)
    show("P' = P @ D  (placement for the kept part):", p_new)
    corner_old = apply(p, part_b[:1])[0]
    corner_new = apply(p_new, part_a[:1])[0]
    print("\nSame point of the part, seen in the parent assembly:")
    print("  duplicate :", np.round(corner_old, 6))
    print("  kept part :", np.round(corner_new, 6))

    # --- Stress test: 1000 random instances -------------------------------
    worst = 0.0
    for _ in range(1000):
        p = make_matrix(rng.uniform(-180, 180, 3), rng.uniform(-2000, 2000, 3))
        world_old = apply(p, part_b)                       # where the duplicate sat
        world_new = apply(new_placement(p, d), part_a)     # where the kept part sits now
        worst = max(worst, float(np.abs(world_old - world_new).max()))

    print(f"\nLargest deviation over 1000 random instances: {worst:.2e}")
    assert worst < 1e-9
    print("OK: the kept part overlaps the old duplicate exactly.")
