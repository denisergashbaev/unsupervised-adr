import torch
from models import actor
from arguments import get_args
import gym
import numpy as np
import os
import os.path as osp
import matplotlib.pyplot as plt
from matplotlib import animation, rc
from scipy.interpolate import spline


def sampling_plot(sampling, sp_index, approach='adr'):

    epoch = [0, 9, 19, 29, 39, 49]
    values = []

    for i, e in enumerate(epoch):
        seed = []
        for s in SEED:
            save_dir = osp.join(args.save_dir, "sp" + str(sp_index) + "polyak" +
                                str(args.polyak) + '-' + str(approach), str(s), args.env_name + '/')
            list_ = []
            for rank in range(8):
                alice_envs = np.load(save_dir + f'adr-sampling_Ep_{e}_R{rank}.npz')
                envs = alice_envs[sampling]

                list_.append(envs)
            list_ = np.reshape(list_, (-1, 1))
            seed.extend(list_)
        samplings = np.reshape(seed, (-1, 1))
        values.append(samplings)
    return values


def genelarization(approach, parameter, selplay_index, epoch=-1):
    evaluations = []
    for s in SEED:
        save_dir = osp.join(args.save_dir, "sp" + str(sp[selplay_index]) + "polyak" +
                            str(args.polyak) + '-' + str(approach), str(s), args.env_name + '/')
        evals = np.load(os.getcwd() + '/' + save_dir + 'success_rates.npy')
        last_eval = evals[epoch]
        evaluations.append(last_eval[parameter][:])
    evaluations_mean = np.mean(evaluations, axis=0)

    evaluations_std = np.std(evaluations, axis=0)

    return evaluations_mean, evaluations_std

if __name__ == '__main__':
    args = get_args()
    # load the model param
    xlabels = np.geomspace(0.05, 1, 10)
    xlabel_learning = np.linspace(1, 50, 2500)
    x_gen_labels = np.linspace(0, 50, 1)
    epoch = [0, 9, 19, 29, 39, 49]
    sp = [0.0, 0.5, 1.0]
    approach = ['udr', "adr", "adr"]
    # PARAMETERS = ["Mass of block", "Mass of hook", "Friction"]
    PARAMETERS = ['Friction']
    plot_type = ['dashed','dashdot', 'solid', '--', ':', '--', '-']
    PLOTCOLORS = ['darkmagenta', 'orange', 'red', 'darkolivegreen', 'hotpink', 'blue']
    # alice_sampling = ['block_mass', 'hook_mass', 'friction']
    alice_sampling = ['friction']
    SEED = [20, 22, 23, 24]

    ######## Plot generalization curve ########

    for i, param in enumerate(PARAMETERS):
        fig, axes = plt.subplots(1, 2)
        for j, e in enumerate(epoch):
            evaluations_mean, evaluations_std = genelarization('adr', i, 1, epoch=e)
            axes[0].plot(xlabels, evaluations_mean, label=f'Epoch : {e}', color=PLOTCOLORS[j], alpha=0.7)
            axes[0].fill_between(xlabels, evaluations_mean - evaluations_std / 2, evaluations_mean + evaluations_std / 2,
                             alpha=0.05, color=PLOTCOLORS[j])

            axes[0].set_xlabel("Multipliers")
            axes[0].set_ylabel("Success Rate")
            axes[0].set_title(f"{param} Generalization for FetchPush Environment")
            axes[0].legend()
        # values = sampling_plot(alice_sampling[i], sp_index=sp[-1], approach='adr')
        # axes[1].hist(values, stacked=True, label=['Epoch :' + str(e) for e in epoch], color=PLOTCOLORS[0:6], alpha=0.4)
        # axes[1].legend()
        # axes[1].set_xlabel("Multipliers")
        # axes[1].set_ylabel("Frequency")
        # axes[1].set_title(f'{param} sampling frequency over time')

        # plt.show()
        plt.clf()   
        plt.close()
    for j, app in enumerate(approach):
        print(app)
        udr_gen, udr_std = genelarization(app, 0, j, epoch=-1)

        plt.plot(xlabels, udr_gen, alpha=0.7, label=f'{app} - sp{sp[j]}')
        plt.fill_between(xlabels, udr_gen - udr_std, udr_gen + udr_std, alpha=0.2)

    plt.legend()
    plt.xlabel("Multipliers")
    plt.ylabel("Success Rate")
    # plt.ylim(0, 1.2)
    plt.show()

    ######## Plot learning curve ########
    learning_params = ["Default Env Success", "Default Env Average Distance", "Hard Env Success", "Hard Env Average Distance"]
    save_dir = osp.join(args.save_dir, "sp" + str(sp[0]) + "polyak" +
                        str(args.polyak) + '-' + str(approach[0]), str(24), args.env_name + '/')
    learning = np.load(os.getcwd() + '/' + save_dir + 'evaluations.npz')
    for i, keys in enumerate(learning.keys()):
        for idx, app in enumerate(approach):
            learnings = []
            for s in SEED:
                save_dir = osp.join(args.save_dir, "sp" + str(sp[idx]) + "polyak" +
                                    str(args.polyak) + '-' + str(approach[idx]), str(s), args.env_name + '/')
                learning = np.load(os.getcwd() + '/' + save_dir + 'evaluations.npz')
                key = learning[keys]
                learnings.append(key)
            learnings_mean = np.mean(learnings, axis=0)
            learnings_std = np.reshape(np.std(learnings, axis=0), (-1))
            y = np.convolve(np.reshape(learnings_mean, (-1)), np.ones(10) / 10)
            plt.plot(xlabel_learning, y[5:2505], label= f"{app} :{keys}", color=PLOTCOLORS[idx])
            # plt.fill_between(xlabel_learning, np.reshape(learnings_mean, (-1))
            #                  - learnings_std / 2, np.reshape(learnings_mean, (-1)) + learnings_std / 2,
            #                  facecolor=PLOTCOLORS[idx], alpha=0.8)
            plt.xlim(0, 50)
            plt.title(f"Learning curve (Noisyhook Environment) : {learning_params[i]}")
            plt.xlabel("Epoch")
            plt.ylabel(f'{learning_params[i]}')
            plt.legend()
        # plt.savefig(f'{keys}.png')
        # plt.show()
        # plt.clf()
    plt.close()

