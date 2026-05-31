from __future__ import annotations

import numpy as np
import numpy.typing as npt
from dataclasses import dataclass, field
from pathlib import Path
from svg.path import parse_path
from xml.dom import minidom


@dataclass
class ComplexPoint:
    point: complex = complex()
    frequency: float = 0
    amplitude: float = field(init=False)
    phase: float = field(init=False)

    def __post_init__(self):
        self.amplitude = np.sqrt(self.point.real**2 + self.point.imag**2)
        self.phase = np.arctan2(self.point.real, self.point.imag)

    def __add__(self, point: ComplexPoint) -> ComplexPoint:
        c = complex(
            self.point.real + point.point.real, self.point.imag + point.point.imag
        )
        return ComplexPoint(c)

    def __mul__(self, point: ComplexPoint) -> ComplexPoint:

        angle = self.phase + point.phase
        real = self.amplitude * point.amplitude * np.cos(angle)
        imag = self.amplitude * point.amplitude * np.sin(angle)

        return ComplexPoint(complex(real, imag))


def read_svg(file_path: str | Path) -> str:
    """
    Reads the svg file from given path and extracts the svg string
    from <path> tag's d-attribute.

    Parameters:
            file_path: str = path to svg file

    Returns:
            svg_string: str
    """

    with open(file_path, "r") as file1:
        data = file1.read()
    svg_file = minidom.parseString(data)
    svg_string = svg_file.getElementsByTagName("path")[0].getAttribute("d")

    return svg_string


def create_discrete_points(
    svg_string: str,
    n_samples: int,
    mirror_wrt_x_axis: bool = True,
    mirror_wrt_y_axis: bool = False,
) -> npt.NDArray[np.complex64]:
    """
    Takes the svg path string and no of samples required as input
    and produces specified number of discrete complex points.

    Now, often discrete points created by the svg string produces
    an image which is mirrored with respect to (w.r.t) the x-axis.
    By tweaking the mirroring booleans this issue can be resolved.

    By default, the points are mirrored with respect to the x-axis.

    Parameters:
            svg_str: str = string retrived from d-attribute of path
                               tag in any svg file

            n_samples: int = number of samples to produce

            mirror_wrt_x_axis: bool [True] = weather or not to mirror
                               the image w.r.t x-axis, default is True

            mirror_wrt_y_axis: bool [False] = weather or not to mirror
                               the image w.r.t y-axis, default is False

    Returns:
            discrete_points: list[complex]
    """

    mx = -1
    my = 1
    if not mirror_wrt_x_axis:
        mx = 1
    if mirror_wrt_y_axis:
        my = -1

    svg_str = parse_path(svg_string)
    discrete_points = [svg_str.point(t) for t in np.linspace(0, 1, n_samples)]
    discrete_points = [complex(my * p.real, mx * p.imag) for p in discrete_points]

    return np.array(discrete_points, dtype=np.complex64)
