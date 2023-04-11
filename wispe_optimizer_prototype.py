import numpy as np
import matplotlib.pyplot as plt

def Q(xp):
    x = np.linspace(0, 10, 101)
    y = 10**(-x*(x-4)*0.1+7 -x*(x-2)*0.05+3)

    return np.interp(xp,x,y)

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

if __name__ == '__main__':

    x_list = np.array([6])
    y_list = Q(x_list)

    for i in range(0,10):

        print(x_list)
        print(y_list)
        print(' ')

        x_guess = WISPE_next_guess(x_list, y_list, guess_step=1)

        x_list = np.append(x_list, x_guess)
        y_list = np.append(y_list, Q(x_guess))

    plt.scatter(x_list,y_list)