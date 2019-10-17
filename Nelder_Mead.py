import numpy as np
from BenchMark_funcs import Five_well_potential_function as target_func

class Nelder_Mead:
    def __init__(self, num_param, seed, mean=0, sigma=1):
        self.num_param = num_param
        self.center = None
        self.P_refl = None
        self.result = None
        self.params = self.initialize_params(seed, mean, sigma)
        
    def initialize_params(self, seed, mean, sigma):
        np.random.seed(seed)
        init_params = np.random.normal(loc=mean,
                                       scale=sigma,
                                       size=(self.num_param+1, self.num_param))
        return init_params

    def func(self, inputs):
        y = target_func(inputs)
        result = np.concatenate([inputs, y], axis=-1)  #([p1, f(p1)],[p2, f(p2)], ..., [pm+1, f(pm+1)])
        return result

    def calc(self, alpha=1):
        self.result = self.result[np.argsort(self.result[:, -1])]#sorted on f(px)
        center = np.mean(self.result[:-1, :self.num_param], axis=0)#, keepdims=True)#Calc center
        self.center = center
        center_h = center - self.result[-1, :self.num_param]
        self.center_h = center_h
        refl_coord = center + alpha * (center_h)#[[p_refl]]
        self.P_refl = self.func(refl_coord[None])[0]#[p_refl, f(p_refl)]
        return 0

    def update_opt(self, beta=2, gamma=-0.5, delta=-0.5):
        self.result = self.func(self.params)
        self.calc()
        #print(self.result)
        #print(self.center)
        #print(self.P_refl)

        if self.P_refl[-1] < self.result[-2, -1] and self.P_refl[-1] >= self.result[0, -1]:
            #print("0")
            self.params = np.concatenate([self.result[:-1, :self.num_param],
                                          self.P_refl[None, :self.num_param]], axis=0)
            
        elif self.P_refl[-1] < self.result[0, -1]:
            expand_coord = self.center + beta * self.center_h
            P_expand = self.func(expand_coord[None])[0]
            #print("P_expand:", P_expand)
            if P_expand[-1] < self.P_refl[-1]:
                #print("1-1")
                self.params = np.concatenate([self.result[:-1, :self.num_param],
                                              P_expand[None, :self.num_param]], axis=0)
            else:
                #print("1-2")
                self.params = np.concatenate([self.result[:-1, :self.num_param],
                                              self.P_refl[None, :self.num_param]], axis=0)
                
        elif self.P_refl[-1] >= self.result[-2, -1]:
            contract_coord = self.center + gamma * self.center_h
            P_contract = self.func(contract_coord[None])[0]
            #print("P_contract:", P_contract)
            if P_contract[-1] < self.result[-1, -1]:
                #print("2-1")
                self.params = np.concatenate([self.result[:-1, :self.num_param],
                                              P_contract[None, :self.num_param]], axis=0)
                #print(self.params)
            else:
                #print("2-2")
                reduct = self.result[1:, :self.num_param] - self.result[:1, :self.num_param]
                reduct = self.result[1:, :self.num_param] + delta * reduct
                #self.result[1:, :self.num_param] + delta * reduct
                self.params = np.concatenate([self.result[:1, :self.num_param],
                                              reduct], axis=0)
                
        else:
            print("[Nelder_Mead]Error...")
            exit()
        #print(self.params)   
        return 0
    
def main(NUM_PARAM, seed, mean, sigma):
    BETA = 2
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()                                                        
    ax = Axes3D(fig)
    x1 = np.linspace(-20, 20, 100)
    x2 = np.linspace(-20, 20, 100)
    X, Y = np.meshgrid(x1, x2)
    inputs = np.stack([X, Y], axis=-1)
    ax.plot_wireframe(X,
                      Y,
                      target_func(inputs)[...,0],
                      alpha=0.5)
    
    a = Nelder_Mead(NUM_PARAM, seed, mean, sigma)
    """
    ax.scatter(a.params[:,0],
               a.params[:,1],
               target_func(a.params)[...,0],
               facecolors='red',
               alpha=1)
    """
    """
    ax.scatter(a.center[0],
               a.center[1],
               target_func(a.center[None])[...,0],
               facecolors='red',
               alpha=1)
    """
    print("init_params:", a.params)
    for i in range(500):
        #print("--------{}--------".format(i))
        a.update_opt(beta=BETA)
        ax.scatter(a.center[0],
                   a.center[1],
                   target_func(a.center[None])[...,0],
                   facecolors='red',
                   alpha=1)
        #print(a.result)
        """
        ax.scatter(a.params[:,0],
                   a.params[:,1],
                   target_func(a.params)[...,0],
                   facecolors='red',
                   alpha=1)
        """
        #plt.pause(0.1)
    print(a.params)
    print(a.result)
    #"""

def scipy_NM(NUM_PARAM, seed, mean, sigma):
    from scipy.optimize import minimize
    #"""
    np.random.seed(seed)
    init_params = np.random.normal(loc=mean,
                                   scale=sigma,
                                   size=(NUM_PARAM+1, NUM_PARAM))
    print("init_params:", init_params)
    res = minimize(target_func, init_params, method='nelder-mead')
    print(res)
    
if __name__ == '__main__':
    main(NUM_PARAM=2, seed=2, mean=0, sigma=10)
    scipy_NM(NUM_PARAM=2, seed=2, mean=0, sigma=10)
    
