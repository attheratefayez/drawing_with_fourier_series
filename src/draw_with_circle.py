# %%
import numpy as np
import numpy.typing as npt
from scipy.fft import fft
from matplotlib import colormaps
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from pathlib import Path

from src.png_to_discrete import image_to_complex_points
from src.utils import read_svg, create_discrete_points, ComplexPoint


import matplotlib.pyplot as plt


class DrawWithCircles:

    def __init__(self, image_path: str | Path, n_points: int = 100):

        self.__supported_types = [".svg", ".png", ".jpg"]
        self.__image_path = (
            image_path if isinstance(image_path, Path) else Path(image_path)
        )
        self.__n_points = n_points
        self.__complex_components = []

        if self.__image_path.suffix not in self.__supported_types:
            raise Exception(
                "File Type not supported. Supported file-types are: .svg, .png, .jpg"
            )

        if not self.__image_path.exists():
            raise FileNotFoundError(
                f"[Error] No file found at: {self.__image_path.absolute()}"
            )

        if self.__image_path.suffix == ".svg":
            svg_string = read_svg(self.__image_path)
            self.__discrete_signal = create_discrete_points(svg_string, self.__n_points)

        else:
            self.__discrete_signal = image_to_complex_points(
                self.__image_path, self.__n_points
            )

    def visualize_signal(self):
        plt.plot(self.__discrete_signal.real, self.__discrete_signal.imag)
        plt.show()

    def _get_complex_components(self, normalize: bool = True, make_sorted: bool = False) :
        complex_components: npt.NDArray[np.complex64] = fft(self.__discrete_signal).astype(np.complex64)

        if normalize:
            complex_components /= self.__discrete_signal.size

        self.__complex_components = []
        for idx, component in enumerate(complex_components):
            self.__complex_components.append(ComplexPoint(component, frequency=idx))

        if make_sorted:
            self.__complex_components.sort(key = lambda x: x.amplitude, reverse=True)

    def draw(self):
        self._get_complex_components()

        fig, ax = plt.subplots()
        ax.set_axis_off()

        colors = colormaps["rainbow"](np.linspace(0, 1, len(self.__complex_components)))

        circles = []
        radius_lines = []

        for idx, component in enumerate(self.__complex_components):
            radius = component.amplitude
            color = colors[idx]

            c = Circle(
                (component.point.real, component.point.imag),
                radius=radius,
                alpha=0.35,
                animated=True,
                fill=False,
                color=color,
            )
            l = Line2D([], [], color=color, alpha=0.5)

            ax.add_patch(c)
            ax.add_line(l)

            circles.append(c)
            radius_lines.append(l)

        (line,) = ax.plot([], [])

        padding = 0.3
        real = self.__discrete_signal.real
        imag = self.__discrete_signal.imag
        r_min, r_max = real.min(), real.max()
        i_min, i_max = imag.min(), imag.max()
        r_span = r_max - r_min or 1
        i_span = i_max - i_min or 1
        ax.set_xlim(r_min - padding * r_span, r_max + padding * r_span)
        ax.set_ylim(i_min - padding * i_span, i_max + padding * i_span)

        drawn_points = np.array([], dtype=np.complex64)


        def update(frame):
            artists = []
            nonlocal drawn_points

            pen_tip = np.complex64()
            last_pen_tip = np.complex64()

            for component, circle, rad_line in zip(self.__complex_components, circles, radius_lines):
                pen_tip += component.point* np.exp(
                    1j * (2 * np.pi * frame * component.frequency) / self.__discrete_signal.size
                )

                if last_pen_tip:
                    circle.center = (last_pen_tip.real, last_pen_tip.imag)
                    circle.radius = component.amplitude
                    rad_line.set_xdata([last_pen_tip.real, pen_tip.real])
                    rad_line.set_ydata([last_pen_tip.imag, pen_tip.imag])

                else:
                    point = component.point
                    circle.center = (point.real, point.imag)
                    circle.radius = component.amplitude
                    rad_line.set_xdata([point.real, pen_tip.real])
                    rad_line.set_ydata([point.imag, pen_tip.imag])

                last_pen_tip = pen_tip

            drawn_points = np.hstack([drawn_points, pen_tip.copy()])

            line.set_xdata(drawn_points.real)
            line.set_ydata(drawn_points.imag)

            print(frame)

            artists.append(line)
            artists.extend(circles)
            artists.extend(radius_lines)

            return artists


        ani = FuncAnimation(
            fig=fig, func=update, frames=self.__discrete_signal.size, interval=95, blit=True
        )
        # plt.show()
        ani.save("some_gif.gif", PillowWriter(fps=10))



if __name__ == "__main__":
    draw = DrawWithCircles("./images_to_try/gear.jpg")
    # draw.visualize_signal()
    draw.draw()
