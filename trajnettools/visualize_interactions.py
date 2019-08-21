import argparse
import math
import numpy as np

from . import load_all
from . import show
from .interactions import *
import matplotlib.pyplot as plt

T_OBS, T_SEQ, T_INT, T_STR = 9, 21, 9,  

def theta_rotation(xy, theta):
    # rotates scene by theta
    
    ct = math.cos(theta)
    st = math.sin(theta)

    r = np.array([[ct, st], [-st, ct]])
    return np.einsum('ptc,ci->pti', xy, r)


def center_scene(path, neigh_path, time_param=(9, 21, 9, 3)):
    ## Centre scene

    T_OBS, T_SEQ, T_INT, T_STR = time_param 
    center = path[T_INT, :]
    path = path - center
    neigh_path = neigh_path - center

    k = T_INT - T_STR
    while sum(path[k, :]==0)==2 and k > 0:
        k -= 1

    if k > 0:
        thet = np.pi + np.arccos((path[k, 1])/(np.linalg.norm([0, -1])*np.linalg.norm(path[k, :])))
        if path[k, 0] < 0:
            thet = -thet
        norm_path = theta_rotation(path[:, np.newaxis, :], thet)
        norm_neigh_path = theta_rotation(neigh_path, thet)
        return norm_path[:, 0], norm_neigh_path
    else:
        return path, neigh_path


def multimodality_plot(input_file, pos_angle=4, pos_range=15, vel_angle=4, vel_range=15, dist_thresh=5, n_theta=15, vr_max=2.5, vr_n=10):
	## Multimodality of interactions
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))

    heatmap = False

    # run
    i = 0
    x_values = []
    y_values = []
    for primary_ped, rows in load_all(input_file):
        path = rows[:, 0]
        neigh_path = rows[:, 1:]
        interaction_matrix = get_interaction_matrix(rows, pos_angle, pos_range, vel_angle, vel_range, dist_thresh, choice='bothpos', output='matrix')
    
        interaction_index = np.any(interaction_matrix, axis=0)

        ## Overall Plot
        # if np.sum(interaction_index) > 0 and np.sum(interaction_index) < 2:
        #     # print(np.sum(interaction_index))
        #     i += 1
        #     neigh = neigh_path[:,interaction_index]
        #     path, neigh = center_scene(path, neigh)
        #     # ax.plot(path[:9, 0], path[:9, 1])
        #     ax.plot(path[T_OBS:, 0], path[T_OBS:, 1])
        #     # ax.plot(neigh[T_OBS:, 0, 0], neigh[T_OBS:, 0, 1])
        #     ## PP
        #     x_values = np.concatenate((x_values, path[T_OBS:, 0]))
        #     y_values = np.concatenate((y_values, path[T_OBS:, 1]))
        #     ## Neighbours 
        #     # x_values = np.concatenate((x_values, neigh[T_OBS:, 0, 0]))
        #     # y_values = np.concatenate((y_values, neigh[T_OBS:, 0, 1]))
        #     # ax.plot(path[0, 0], path[0, 1], color='g', marker='o', label = 'start point')
        #     # ax.plot(path[-1, 0], path[-1, 1], color='r', marker='x', label = 'end point')
        #     # ax.plot(neigh[:, 0, 0], neigh[:, 0, 1])
        #     # ax.plot(neigh[0, 0, 0], neigh[0, 0, 1], color='g', marker='o', label = 'start point')
        #     # ax.plot(neigh[-1, 0, 0], neigh[-1, 0, 1], color='r', marker='x', label = 'end point')
        #     ax.set_xlim([-6, 6])
        #     ax.set_ylim([-6, 6])

        ## 5 Examples of interactions ##
        if (np.sum(interaction_index) == 1) & (np.linalg.norm(path[-1] - path[0]) > 1.0):
            i += 1
            if i < 25:
                neigh = neigh_path[:,interaction_index]
                path, neigh = center_scene(path, neigh)
                ax.plot(path[:, 0], path[:, 1])
                # ax.plot(path[:T_OBS, 0], path[:T_OBS, 1])
                # ax.plot(path[T_OBS:, 0], path[T_OBS:, 1])
                ax.plot(neigh[:, 0, 0], neigh[:, 0, 1])
                ## PP
                # x_values = np.concatenate((x_values, path[T_OBS:, 0]))
                # y_values = np.concatenate((y_values, path[T_OBS:, 1]))
                ## Neighbours 
                # x_values = np.concatenate((x_values, neigh[T_OBS:, 0, 0]))
                # y_values = np.concatenate((y_values, neigh[T_OBS:, 0, 1]))
                # ax.plot(path[0, 0], path[0, 1], color='g', marker='o', label = 'start point')
                ax.plot(path[-1, 0], path[-1, 1], color='r', marker='x', label = 'end point')
                # ax.plot(neigh[:, 0, 0], neigh[:, 0, 1])
                # ax.plot(neigh[0, 0, 0], neigh[0, 0, 1], color='g', marker='o', label = 'start point')
                ax.plot(neigh[-1, 0, 0], neigh[-1, 0, 1], color='r', marker='x', label = 'end point')
                ax.set_xlim([-10, 10])
                ax.set_ylim([-10, 10])
                fig.show()
                ax.clear()

    print("Number of Instances: ", i) 

    if heatmap:
	    ax.clear()
	    heatmap, xedges, yedges = np.histogram2d(y_values, x_values, bins=[50, 50], range=[[-3,3],[-3,3]])
	    thres = 10
	    heatmap[np.where(heatmap >= thres)] = thres
	    plt.imshow(heatmap, interpolation='none', origin='lower')
	    plt.colorbar()

    fig.show()
    plt.close(fig)


def dataset_plots(input_file, pos_angle=4, pos_range=15, vel_angle=4, vel_range=15, dist_thresh=5, n_theta=360, vr_max=2.5, vr_n=10, choice='pos'):
	## Distributions of interactions
	## choice : Choice of angle to be thresholded 
			# 'pos': Angle between Velocity of PP and Line Joining PP to N
			# 'vel': Angle between Velocity of PP and Velocity of N 
			# 'pos_vel': Both pos and vel 

    ## choice: 'pos'
    ## The radial plot shows the interaction map on ground plane. Viz 1
    ## The mean plot shows the distance as a function of angle. Viz 2


    ## choice: 'vel'
    ## The radial plot shows the interaction map. Viz 1
    ## The mean plot shows the distance as a function of relative velocity. Viz 4
    
    distr = np.zeros((n_theta, vr_n))
    def fill_grid(theta_vr):
        theta, vr, sign = theta_vr
        theta = theta*(2*np.pi)/360
        # theta[np.where(sign < 0)] = (2*np.pi - 1/n_theta) - theta[np.where(sign < 0)]
        thetap = np.floor(theta * distr.shape[0] / (2*np.pi)).astype(int)
        vrp = np.floor(vr * distr.shape[1] / dist_thresh).astype(int)
        distr[thetap, vrp] += 1
    
    unbinned_vr = [[] for _ in range(n_theta)]
    def fill_unbinned_vr(theta_vr):
        theta, vr, sign = theta_vr
        theta = theta*(2*np.pi)/360
        # theta[np.where(sign < 0)] = (2*np.pi - 1/n_theta) - theta[np.where(sign < 0)]
        thetap = np.floor(theta * len(unbinned_vr) / (2*np.pi)).astype(int)
        for th in range(len(thetap)):
            unbinned_vr[thetap[th]].append(vr[th])

    vr_max = dist_thresh
    i = 0
    for primary_ped, rows in load_all(input_file):
        interaction_matrix, chosen_true, sign_true, dist_true = \
        get_interaction_matrix(rows, pos_angle, pos_range, vel_angle, vel_range, dist_thresh, choice)

        fill_grid((chosen_true, dist_true, sign_true))
        fill_unbinned_vr((chosen_true, dist_true, sign_true))      

    with show.canvas(input_file + '.' + choice + '.png', figsize=(4, 4), subplot_kw={'polar': True}) as ax:
        r_edges = np.linspace(0, vr_max, distr.shape[1] + 1)
        theta_edges = np.linspace(0, 2*np.pi, distr.shape[0] + 1)
        thetas, rs = np.meshgrid(theta_edges, r_edges)
        ax.pcolormesh(thetas, rs, distr.T, vmin=0, vmax=None, cmap='Blues')

        median_vr = np.array([np.median(vrs) if len(vrs) > 5 else np.nan
                              for vrs in unbinned_vr])
        center_thetas = np.linspace(0.0, 2*np.pi, len(median_vr) + 1)
        center_thetas = 0.5 * (center_thetas[:-1] + center_thetas[1:])
        # close loop
        center_thetas = np.hstack([center_thetas, center_thetas[0:1]])
        median_vr = np.hstack([median_vr, median_vr[0:1]])
        # plot median radial velocity
        # ax.plot(center_thetas, median_vr, label='median $d_r$ [m/s]', color='orange')

        ax.grid(linestyle='dotted')
        ax.legend()    

def group_plots(input_file, dist_thresh=0.8, std_thresh=0.1):
    ## Identify and Visualize Groups
    ## dist_thresh: Distance threshold to be withinin a group
    ## std_thresh: Std deviation threshold for variation of distance
    
    i = 0
    j = 0
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    for primary_ped, rows in load_all(input_file):
        path, group, flag = check_group(rows, dist_thresh, std_thresh)
        # print("Group Shape", group.shape, group.shape[1])
        
        if flag:
            i += 1
            if np.linalg.norm(path[-1] - path[0]) < 1.0:
                j += 1
            if i < 15:
                # path, neigh = center_scene(path, neigh)
                # ax.plot(path[:T_OBS, 0], path[:T_OBS, 1])
                ax.plot(path[T_OBS:, 0], path[T_OBS:, 1])
                for j in range(group.shape[1]):
                    ax.plot(group[T_OBS:, j, 0], group[T_OBS:, j, 1])

                ## PP
                # x_values = np.concatenate((x_values, path[T_OBS:, 0]))
                # y_values = np.concatenate((y_values, path[T_OBS:, 1]))

                ## Neighbours 
                # x_values = np.concatenate((x_values, neigh[T_OBS:, 0, 0]))
                # y_values = np.concatenate((y_values, neigh[T_OBS:, 0, 1]))

                # ax.plot(path[0, 0], path[0, 1], color='g', marker='o', label = 'start point')
                ax.plot(path[-1, 0], path[-1, 1], color='r', marker='x', label = 'end point')

                # ax.plot(neigh[:, 0, 0], neigh[:, 0, 1])
                # ax.plot(neigh[0, 0, 0], neigh[0, 0, 1], color='g', marker='o', label = 'start point')
                ax.plot(group[-1, 0, 0], group[-1, 0, 1], color='r', marker='x', label = 'end point')
                # ax.set_xlim([-10, 10])
                # ax.set_ylim([-10, 10])
                plt.axis('equal')
                fig.show()
                ax.clear()
    print("Number of Groups: ", i)
    print("Number of Stationary Groups: ", j)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_files', nargs='+',
                        help='Trajnet dataset file(s).')
    args = parser.parse_args()

    print('{dataset:>60s} |     N'.format(dataset=''))
    for dataset_file in args.dataset_files:
        print('{dataset:>60s} | {N:>5}'.format(
            dataset=dataset_file,
            N=sum(1 for _ in load_all(dataset_file)),
        ))

    pos_angle = 0
    vel_angle = 180
    pos_range = 15
    vel_range = 10
    dist_thresh = 4
    n_theta = 72
    vr_max = 2.5
    vr_n = 10
    for dataset_file in args.dataset_files:
        # pass

        # Interaction
        # multimodality_plot(dataset_file, pos_angle, pos_range, vel_angle, vel_range, dist_thresh, n_theta, vr_max, vr_n)

        # for vel_angle in [0, 180]:
        #     print("VEL Angle: ", vel_angle)
        #     for dist_thresh in range(1, 5):
        #         print("Dist Thresh:", dist_thresh)
        #         multimodality_plot(dataset_file, pos_angle, pos_range, vel_angle, vel_range, dist_thresh, n_theta, vr_max, vr_n)


        # # Position Global 
        # dataset_plots(dataset_file, pos_angle, pos_range, vel_angle, vel_range, dist_thresh, n_theta, vr_max, vr_n, 'pos')
        
        # # Positions for Agents moving in same direction
        # dataset_plots(dataset_file, pos_angle, pos_range, 180, 10, dist_thresh, n_theta, vr_max, vr_n, 'bothpos')

        # # Positions for Agents moving in opposite direction
        # dataset_plots(dataset_file, pos_angle, pos_range, 0, 10, dist_thresh, n_theta, vr_max, vr_n, 'bothpos')

        # # Velocity Global
        # dataset_plots(dataset_file, pos_angle, pos_range, vel_angle, vel_range, dist_thresh, n_theta, vr_max, vr_n, 'vel')
        
        # # Velocity for Agents in Front
        # dataset_plots(dataset_file, 0, 10, vel_angle, vel_range, dist_thresh, n_theta, vr_max, vr_n, 'bothvel')

        # Grouping
        group_plots(dataset_file)

if __name__ == '__main__':
    main()
