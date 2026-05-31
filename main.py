from src.draw_with_circle import DrawWithCircles

dwc = DrawWithCircles("/home/fayez/Bugs/pythonworks/dft_drawing/images_to_try/svg_files/Maple_Leaf.svg", 300)
dwc.draw()



# import components as com
# import matplotlib.pyplot as plt
#
# svg_path_d = com.read_svg('./svg_files/bat.svg')
#
# # WITHOUT MIRRORING THE POINTS
# # discrete_points = com.create_discrete_points(svg_path_d, 150, mirror_wrt_x_axis=False)
#
# discrete_points = com.create_discrete_points(svg_path_d, 150, mirror_wrt_y_axis=True)
# # fig, ax = plt.subplots()
#
# # fig.set_facecolor('slategrey')
# # ax.set_facecolor('slategrey')
#
# # ax.plot(
# # 	[p.real for p in discrete_points],
# # 	[p.imag for p in discrete_points],
# # 	marker = '.',
# # 	color = 'crimson'
# # )
#
# # plt.show()
#
# cn = com.dft(discrete_points)
# com.draw_with_coefficients(cn, animated=False)
