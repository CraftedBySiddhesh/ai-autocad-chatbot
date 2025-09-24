import argparse
from pathlib import Path

from core.dxf_writer import render
from core.nlp_rules import parse


def make_preview(program, png_path: Path):
    import math

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = plt.gca()

    for c in program.circles:
        th = [t / 180 * math.pi for t in range(0, 361)]
        xs = [c.x + c.r * math.cos(t) for t in th]
        ys = [c.y + c.r * math.sin(t) for t in th]
        ax.plot(xs, ys)
    for line in program.lines:
        ax.plot([line.x1, line.x2], [line.y1, line.y2])
    for r in program.rects:
        xs = [r.x, r.x + r.w, r.x + r.w, r.x, r.x]
        ys = [r.y, r.y, r.y + r.h, r.y + r.h, r.y]
        ax.plot(xs, ys)
    for a in program.arcs:
        th = [t / 180 * math.pi for t in range(int(a.a1), int(a.a2) + 1)]
        xs = [a.x + a.r * math.cos(t) for t in th]
        ys = [a.y + a.r * math.sin(t) for t in th]
        ax.plot(xs, ys)
    for pl in program.polylines:
        xs = [p[0] for p in pl.pts]
        ys = [p[1] for p in pl.pts]
        if pl.closed and pl.pts and pl.pts[0] != pl.pts[-1]:
            xs.append(pl.pts[0][0])
            ys.append(pl.pts[0][1])
        ax.plot(xs, ys)
    for e in program.ellipses:
        th = [t / 180 * math.pi for t in range(0, 361)]
        xs = [e.x + e.rx * math.cos(t) for t in th]
        ys = [e.y + e.ry * math.sin(t) for t in th]
        ax.plot(xs, ys)
    for tx in program.texts:
        ax.text(tx.x, tx.y, tx.text, fontsize=8)

    ax.set_aspect('equal', adjustable='box')
    ax.grid(True)
    fig.savefig(png_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Natural language drawing command (quote it)")
    parser.add_argument("--preview", action="store_true", help="Save a PNG preview next to the DXF")
    args = parser.parse_args()

    program = parse(args.command)

    print(
        f"Summary -> circles:{len(program.circles)} lines:{len(program.lines)} rects:{len(program.rects)} arcs:{len(program.arcs)} plines:{len(program.polylines)} ellipses:{len(program.ellipses)} texts:{len(program.texts)}"
    )
    if not (
        program.circles
        or program.lines
        or program.rects
        or program.arcs
        or program.polylines
        or program.ellipses
        or program.texts
    ):
        print("No entities parsed from your command. Nothing to draw.")
        raise SystemExit(2)

    out = render(program)
    print(f"DXF saved to: {out}")

    if args.preview:
        png_path = Path(out).with_suffix(".png")
        make_preview(program, png_path)
        print(f"Preview saved to: {png_path}")


if __name__ == '__main__':
    main()
