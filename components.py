#%%
from __future__ import annotations
from dataclasses import dataclass, field
from svg.path import parse_path
from xml.dom import minidom
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolor


@dataclass
class ComplexPoint:
	real: float = 0
	imag: float = 0
	magnitude: float = field(init=False)
	phase: float = field(init=False)

	def __post_init__(self):
		self.magnitude = np.sqrt(self.real**2 + self.imag**2)
		self.phase = np.arctan2(self.real,self.imag)
	
	def __add__(self, point: complex | ComplexPoint) -> ComplexPoint:
		return ComplexPoint(self.real + point.real, self.imag + point.imag)
	
	def __mul__(self, point: complex | ComplexPoint) -> ComplexPoint:
		
		if not isinstance(point, ComplexPoint):
			point = ComplexPoint(point.real, point.imag)
		
		angle = self.phase + point.phase
		real = self.magnitude * point.magnitude * np.cos(angle)
		imag = self.magnitude * point.magnitude * np.sin(angle)

		return ComplexPoint(real, imag)


def read_svg(file_path: str) -> str:
	"""
	Reads the svg file from given path and extracts the svg string 
	from <path> tag's d-attribute.
	
	Parameters: 
		file_path: str = path to svg file
	
	Returns:
		svg_string: str
	"""

	with open(file_path, 'r') as file1:
		data = file1.read()
	svg_file = minidom.parseString(data)
	svg_string = svg_file.getElementsByTagName('path')[0].getAttribute('d')

	return svg_string


def create_discrete_points(svg_str: str, n_samples: int, mirror_wrt_x_axis: bool = True, mirror_wrt_y_axis: bool = False) -> list[complex]:
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
	if not mirror_wrt_x_axis: mx = 1
	if mirror_wrt_y_axis: my = -1

	svg_str = parse_path(svg_str)
	discrete_points = [svg_str.point(t) for t in np.linspace(0, 1, n_samples)]
	discrete_points = [complex(my*p.real, mx*p.imag) for p in discrete_points]

	return discrete_points


def dft(discrete_points: complex | ComplexPoint) -> list[ComplexPoint]:
	"""
	Performs Discrete Fourier Transform over the given points and 
	returns the complex frequency values.

	Parameters: 
		discrete_points: complex | ComplexPoint 
	
	Returns:
		coefficients: list[ComplexPoint]
	"""

	coefficients =  []
	for k in range(len(discrete_points)):
		
		cn = 0
		for inx, point in enumerate(discrete_points):
			cn += point * np.exp(-1j*2*np.pi*k*inx/len(discrete_points))		
		coefficients.append(ComplexPoint(cn.real/len(discrete_points), cn.imag/len(discrete_points)))
	
	return coefficients


def draw_with_coefficients(coefficients: ComplexPoint, animated: bool = True):
	"""
	Takes in the complex frequency components, re-constructs the signal
	and plots it.

	Parameters:
		coefficients: ComplexPoints = Complex Frequency Components
		animated: 
	
	Returns: None
	"""
	LIMIT = (max(coefficients, key=lambda x : x.magnitude).magnitude + 800)
	N_Samples = len(coefficients)


	def draw():
		re_vals = []
		im_vals = []

		for t in range(N_Samples):
			point = ComplexPoint() 

			for inx, cn in enumerate(coefficients):
				point += cn*np.exp(1j*inx*2*np.pi*t/N_Samples)
			
			re_vals.append(point.real)
			im_vals.append(point.imag)
		
		fig, ax = plt.subplots()
		fig.set_size_inches(12.5, 12.5)
		fig.set_facecolor(mcolor.CSS4_COLORS['black'])
		ax.set_facecolor(mcolor.CSS4_COLORS['black'])

		ax.plot(re_vals, im_vals)
		plt.show()
	

	def animated_draw():

		re_vals = []
		im_vals = []

		fig, ax = plt.subplots()
		fig.set_size_inches(12.5, 12.5)
		fig.set_facecolor(mcolor.CSS4_COLORS['black'])
		ax.set_facecolor(mcolor.CSS4_COLORS['black'])

		for t in range(N_Samples):

			ax.clear()
			ax.set_xlim((-LIMIT, LIMIT))
			ax.set_ylim((-LIMIT, LIMIT))
			prev_point = ComplexPoint()
			point = ComplexPoint()

			for inx, cn in enumerate(coefficients):
					
				point += cn*np.exp(1j*inx*2*np.pi*t/N_Samples)
				cn = ComplexPoint(cn.real, cn.imag)
				point = ComplexPoint(point.real, point.imag)

				if not inx:
					ax.add_patch(plt.Circle((0, 0), cn.magnitude, fill = False, color=mcolor.CSS4_COLORS['skyblue'], alpha = 0.7))
					ax.plot([0, point.real], [0, point.imag], alpha=0.9)
				else:	
					ax.add_patch(plt.Circle((prev_point.real, prev_point.imag), cn.magnitude, fill = False, color=mcolor.CSS4_COLORS['skyblue'], alpha = 0.7))
					ax.plot([prev_point.real, point.real], [prev_point.imag, point.imag], color = 'white', alpha=0.9)

				if (inx == N_Samples-1):
					ax.scatter(point.real, point.imag, marker = '.', color='red')
				prev_point = point
			
			re_vals.append(point.real)
			im_vals.append(point.imag)
			ax.plot(re_vals, im_vals, color = 'yellow')
			plt.pause(1e-12)

			if t == 0:
				input("Press Enter to start show...")
			print(f"{t}: ({point.real}, {point.imag})")
			

		input("Press Enter to close...")
	
	if animated:
		animated_draw()
	else:
		draw()
