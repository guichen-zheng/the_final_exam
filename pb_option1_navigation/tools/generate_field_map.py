#!/usr/bin/env python3
"""Generate a 2D occupancy map from a field STL mesh.

The field meshes in this workspace are mostly static competition geometry.
For Nav2 we only need a top-down occupancy projection, so this script marks
any triangle that intersects a configurable height band as occupied.
"""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


STL_DTYPE = np.dtype(
    [
        ("normal", "<f4", 3),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", required=True, help="Path to binary STL mesh")
    parser.add_argument("--output-image", required=True, help="Output PGM path")
    parser.add_argument("--output-yaml", required=True, help="Output YAML path")
    parser.add_argument("--resolution", type=float, default=0.05, help="Map resolution in meters")
    parser.add_argument("--padding", type=float, default=0.5, help="Extra border around the mesh")
    parser.add_argument("--model-x", type=float, default=0.0, help="Model pose x in world coordinates")
    parser.add_argument("--model-y", type=float, default=0.0, help="Model pose y in world coordinates")
    parser.add_argument("--model-z", type=float, default=0.0, help="Model pose z in world coordinates")
    parser.add_argument("--z-low", type=float, default=0.05, help="Min height to consider occupied")
    parser.add_argument("--z-high", type=float, default=1.5, help="Max height to consider occupied")
    parser.add_argument(
        "--floor-eps",
        type=float,
        default=0.03,
        help="Treat near-flat low triangles below this thickness as floor and ignore them",
    )
    parser.add_argument(
        "--free-value",
        type=int,
        default=254,
        help="PGM value for free space",
    )
    parser.add_argument(
        "--occupied-value",
        type=int,
        default=0,
        help="PGM value for occupied space",
    )
    return parser.parse_args()


def load_binary_stl(mesh_path: Path) -> np.ndarray:
    with mesh_path.open("rb") as stream:
        stream.read(80)
        triangle_count = struct.unpack("<I", stream.read(4))[0]
        return np.fromfile(stream, dtype=STL_DTYPE, count=triangle_count)


def write_yaml(yaml_path: Path, image_name: str, resolution: float, origin_x: float, origin_y: float) -> None:
    yaml_path.write_text(
        "\n".join(
            [
                f"image: {image_name}",
                "mode: trinary",
                f"resolution: {resolution:.6f}",
                f"origin: [{origin_x:.6f}, {origin_y:.6f}, 0.0]",
                "negate: 0",
                "occupied_thresh: 0.65",
                "free_thresh: 0.25",
                "",
            ]
        )
    )


def main() -> int:
    args = parse_args()

    mesh_path = Path(args.mesh)
    output_image = Path(args.output_image)
    output_yaml = Path(args.output_yaml)
    output_image.parent.mkdir(parents=True, exist_ok=True)
    output_yaml.parent.mkdir(parents=True, exist_ok=True)

    data = load_binary_stl(mesh_path)
    triangles = data["vertices"].copy()
    triangles += np.array([args.model_x, args.model_y, args.model_z], dtype=np.float32)

    flat_vertices = triangles.reshape(-1, 3)
    mins = flat_vertices.min(axis=0)
    maxs = flat_vertices.max(axis=0)

    origin_x = math.floor((float(mins[0]) - args.padding) / args.resolution) * args.resolution
    origin_y = math.floor((float(mins[1]) - args.padding) / args.resolution) * args.resolution
    width = int(math.ceil((float(maxs[0]) - origin_x + args.padding) / args.resolution))
    height = int(math.ceil((float(maxs[1]) - origin_y + args.padding) / args.resolution))

    image = Image.new("L", (width, height), color=args.free_value)
    draw = ImageDraw.Draw(image)

    def to_pixel(x: float, y: float) -> tuple[float, float]:
        px = (x - origin_x) / args.resolution
        py = height - 1 - (y - origin_y) / args.resolution
        return float(px), float(py)

    occupied_triangles = 0
    for triangle in triangles:
        z_min = float(triangle[:, 2].min())
        z_max = float(triangle[:, 2].max())
        if z_max < args.z_low or z_min > args.z_high:
            continue
        if z_max - z_min < args.floor_eps and z_max < 0.35:
            continue
        polygon = [to_pixel(x, y) for x, y, _ in triangle]
        draw.polygon(polygon, fill=args.occupied_value)
        occupied_triangles += 1

    image.save(output_image)
    write_yaml(output_yaml, output_image.name, args.resolution, origin_x, origin_y)

    print(f"Generated {output_image} ({width}x{height}) from {occupied_triangles} projected triangles")
    print(f"Origin: ({origin_x:.3f}, {origin_y:.3f}), resolution: {args.resolution:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
