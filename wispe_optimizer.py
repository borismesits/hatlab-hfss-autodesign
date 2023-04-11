import numpy as np
import matplotlib.pyplot as plt


def WISPE_next_guess(x_list, y_list, guess_step=1):
    
    x_guess = x_list[-1]

    if len(x_list) == 1:
        x_guess = x_list[-1] + guess_step
        
    elif np.where(y_list == np.max(y_list))[0][0] == np.where(x_list == np.min(x_list))[0][0]:
        x_guess = np.min(x_list) - guess_step
        
    elif np.where(y_list == np.max(y_list))[0][0] == np.where(x_list == np.max(x_list))[0][0]:
        x_guess = np.max(x_list) + guess_step
        
    else:
        index_highest = np.argsort(y_list)[-1]
        index_second = np.argsort(y_list)[-2]

        x_guess = (x_list[index_highest] + x_list[index_second])/2
        
    return x_guess