# plm-instance-offset

How to replace a duplicated part by the part you keep, in thousands of released
assemblies, without moving it by a single millimetre.

When two PLM systems are merged, the same standard part (nut, bolt, clamp, cable)
can arrive twice with different origins. Swapping one for the other in an assembly
would shift it. The fix is to measure the origin offset **once per pair** and apply
it to every instance.

## The idea

Use the column-vector convention, where a 4x4 matrix `T` maps local coordinates to
the parent: `x_parent = T @ x_local`.

1. In an empty product, leave the duplicate **B** at the origin and move the part
   you keep, **A**, until it lies exactly on top of B. The placement of A after the
   move is the offset matrix **D**, so `x_B = D @ x_A`.
2. For every instance of B in a parent, read its placement matrix **P**.
3. The kept part gets the placement **P' = P @ D**.

If you do it the other way round (move the duplicate onto the kept part), the
measured matrix is the inverse of D, and the formula becomes
`P' = P @ inverse(D_measured)`. Row-vector conventions swap the multiplication order.
Always check numerically that the two parts overlap before running at scale.

## Run the check

```
pip install numpy
python instance_offset.py
```

The script first walks through one example instance, then runs a stress test. It builds a randomly generated part, an example offset and 1,000 random placements,
replaces the duplicate with the kept part and prints the largest deviation
(around 1e-13, i.e. floating-point noise).

Example output:

```
Example: one instance of the duplicate in a parent assembly

D  (offset, measured once per pair):
       0.000      -1.000       0.000      12.500
       1.000       0.000       0.000      -3.000
       0.000       0.000       1.000      40.000
       0.000       0.000       0.000       1.000
P  (placement of the duplicate in the parent):
       0.814      -0.441       0.379     500.000
       0.470       0.883       0.018     250.000
      -0.342       0.163       0.925      80.000
       0.000       0.000       0.000       1.000
P' = P @ D  (placement for the kept part):
      -0.441      -0.814       0.379     526.636
       0.883      -0.470       0.018     253.947
       0.163       0.342       0.925     112.252
       0.000       0.000       0.000       1.000

Same point of the part, seen in the parent assembly:
  duplicate : [516.506416 249.793908 108.785805]
  kept part : [516.506416 249.793908 108.785805]

Largest deviation over 1000 random instances: 2.27e-13
OK: the kept part overlaps the old duplicate exactly.
```

## Notes

- All data here is randomly generated. No real parts, matrices or company systems are involved.
- The result of this approach in practice: about 229,000 instances across about
  15,000 assemblies updated with a script instead of by hand. Background and
  numbers are in the write-up:
  [1,600 duplicate parts, 229,000 placements](https://ugurakoglu.com/writing/merging-duplicate-parts-with-mql.html).
- Reading and writing the matrices depends on your PLM system's API and is outside
  the scope of this repository.

Uğur Akoğlu · [ugurakoglu.com](https://ugurakoglu.com)
