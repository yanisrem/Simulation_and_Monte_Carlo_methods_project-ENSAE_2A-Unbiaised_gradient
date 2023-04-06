from src.densite_function import *
from src.gaussian_simulation import *
import numpy as np
from src.vraisemblance import *
from scipy.stats import geom

########## Log-vraisemblance
#### IWAE

def importance_sampling_logvraisemblance(k, theta, A, b, x, return_weights=False):
    array_w=np.array([])
    i=0
    while i<k:
        z_i=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]
        W_i=w(z=z_i, x=x, theta=theta, A=A,b=b)
        array_w= np.append (array_w, W_i)
        i+=1
    
    if return_weights:
        return np.log(np.mean(array_w)), array_w
    else:
        return(np.log(np.mean(array_w)))

#### SUMO

def estimateur_SUMO_logvraisemblance(x, theta, A, b, r):
    K=np.random.geometric(p=0.6, size=1)[0]
    k=0
    array_delta_k=np.array([])
    array_proba_K_sup_k=np.array([])

    while k<=K:

        if k==K:
            l_k2, array_w1=importance_sampling_logvraisemblance(k=k+2, theta=theta, A=A, b=b, x=x, return_weights=True)
            l_k1, array_w2=importance_sampling_logvraisemblance(k=k+1, theta=theta, A=A, b=b, x=x, return_weights=True)
            array_w=np.append(array_w1, array_w2)
        else:
            l_k2=importance_sampling_logvraisemblance(k=k+2, theta=theta, A=A, b=b, x=x)
            l_k1=importance_sampling_logvraisemblance(k=k+1, theta=theta, A=A, b=b, x=x)
            
        delta_k=l_k2-l_k1

        if k==0:
            proba_k=1
        else:
            proba_k=geom.cdf(k, p=r)

        array_delta_k=np.append(array_delta_k, delta_k)
        array_proba_K_sup_k=np.append(array_proba_K_sup_k, proba_k)

        k+=1
    
    I_0=np.mean(np.log(array_w))
    SUMO=I_0+np.sum(array_delta_k/array_proba_K_sup_k)

    return SUMO

#### ML-SS

def estimateur_ML_SS_logvraisemblance(x, theta, A, b, r):
    K=np.random.geometric(p=0.6, size=1)[0]

    z_O=np.array([])
    z_E=np.array([])

    array_w=np.array([])
    array_w_O=np.array([])
    array_w_E=np.array([])

    i=0
    while i<2**K:
        z_i_O=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]
        z_i_E=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]

        w_i_E=w(z=z_i_E, x=x, theta=theta, A=A,b=b)
        w_i_O=w(z=z_i_O, x=x, theta=theta, A=A,b=b)

        
        z_O= np.append(z_O, z_i_O)
        z_E= np.append(z_E, z_i_E)

        array_w_O=np.append(array_w_O, w_i_O)
        array_w_E=np.append(array_w_E, w_i_E)
        i+=1

    array_z=np.union1d(z_O, z_E)
    array_w=np.union1d(array_w_O, array_w_E)

    I_0=np.mean(np.log(array_w))

    IWAE_O=np.mean(np.log(array_w_O))
    IWAE_E=np.mean(np.log(array_w_E))
    IWAE_OUE=np.mean(np.log(array_w))

    delta_K=IWAE_OUE-0.5*(IWAE_O+IWAE_E)

    SS=I_0+delta_K/geom.pmf(K, p=r)

    return SS


#### ML-RR

def estimateur_ML_RR_logvraisemblance(x, theta, A, b, r):
    K=np.random.geometric(p=0.6, size=1)[0]
    k=0
    array_delta_k=np.array([])
    array_proba_K_sup_k=np.array([])

    while k<K:

        z_O=np.array([])
        z_E=np.array([])

        array_w=np.array([])
        array_w_O=np.array([])
        array_w_E=np.array([])

        i=0
        while i<2**K:

            z_i_O=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]
            z_i_E=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]

            w_i_E=w(z=z_i_E, x=x, theta=theta, A=A,b=b)
            w_i_O=w(z=z_i_O, x=x, theta=theta, A=A,b=b)

            
            z_O= np.append(z_O, z_i_O)
            z_E= np.append(z_E, z_i_E)

            array_w_O=np.append(array_w_O, w_i_O)
            array_w_E=np.append(array_w_E, w_i_E)
            i+=1

        array_z=np.union1d(z_O, z_E)
        array_w=np.union1d(array_w_O, array_w_E)

        IWAE_O=np.mean(np.log(array_w_O))
        IWAE_E=np.mean(np.log(array_w_E))
        IWAE_OUE=np.mean(np.log(array_w))

        delta_k=IWAE_OUE-0.5*(IWAE_O+IWAE_E)

        if k==0:
            proba_k=1 #convention P(X>=0)=1
        else:
            proba_k=geom.cdf(k, p=r)

        array_delta_k=np.append(array_delta_k, delta_k)
        array_proba_K_sup_k=np.append(array_proba_K_sup_k, proba_k)

        k+=1
    
    I_0=np.mean(np.log(array_w))
    RR=I_0+np.sum(array_delta_k/array_proba_K_sup_k)

    return RR


########## Gradient de la  log-vraisemblance

#### IWAE

def importance_sampling_gradientlogvraisemblance(k, theta, A, b, x, return_z_theta=False):

    array_w=np.array([])
    array_z_theta=np.array([])

    i=0
    while i<k:
        z_i=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]
        W_i=w(z=z_i, x=x, theta=theta, A=A,b=b)
        array_w= np.append(array_w, W_i)

        if i==0:
            array_z_theta=np.append(array_z_theta, z_i-theta)
        else:
            array_z_theta=np.vstack((array_z_theta, z_i-theta))
        i+=1
    
    num=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w,array_z_theta)]), axis=0)
    denom=np.sum(array_w)

    if return_z_theta:
        return num/denom, array_z_theta
    else:

        return num/denom

#### SUMO

def estimateur_SUMO_gradientlogvraisemblance(x, theta, A, b, r):
    K=np.random.geometric(p=0.6, size=1)[0]
    k=0
    array_delta_k=np.array([])
    array_proba_K_sup_k=np.array([])

    while k<=K:

        if k==K:
            gradient_k2, array_z1=importance_sampling_gradientlogvraisemblance(k=k+2, theta=theta, A=A, b=b, x=x, return_z_theta=True)
            gradient_k1, array_z2=importance_sampling_gradientlogvraisemblance(k=k+1, theta=theta, A=A, b=b, x=x, return_z_theta=True)
            array_z=np.vstack((array_z1, array_z2))
        else:
            gradient_k2=importance_sampling_gradientlogvraisemblance(k=k+2, theta=theta, A=A, b=b, x=x)
            gradient_k1=importance_sampling_gradientlogvraisemblance(k=k+1, theta=theta, A=A, b=b, x=x)
            
        delta_k=gradient_k2-gradient_k1

        if k==0:
            proba_k=1
        else:
            proba_k=geom.cdf(k, p=r)

        if k==0:
            array_delta_k=np.append(array_delta_k, delta_k)
        else:
            array_delta_k=np.vstack((array_delta_k, delta_k))

        array_proba_K_sup_k=np.append(array_proba_K_sup_k, proba_k)

        k+=1
    
    I_0=np.mean(array_z, axis=0)
    SUMO=I_0+np.sum(np.array([array_delta_k[i]/array_proba_K_sup_k[i] for i in range(len(array_proba_K_sup_k))]), axis=0)

    return SUMO

#### ML-SS

def estimateur_ML_SS_gradientlogvraisemblance(x, theta, A, b, r):
    K=np.random.geometric(p=0.6, size=1)[0]

    z_O_theta=np.array([])
    z_E_theta=np.array([])

    array_w=np.array([])
    array_w_O=np.array([])
    array_w_E=np.array([])

    i=0
    while i<2**K:
        z_i_O=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]
        z_i_E=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]

        w_i_E=w(z=z_i_E, x=x, theta=theta, A=A,b=b)
        w_i_O=w(z=z_i_O, x=x, theta=theta, A=A,b=b)

        if i==0:
            z_O_theta= np.append(z_O_theta, z_i_O-theta)
            z_E_theta= np.append(z_E_theta, z_i_E-theta)

        else:
            z_O_theta= np.vstack((z_O_theta, z_i_O-theta))
            z_E_theta= np.vstack((z_E_theta, z_i_E-theta))

        array_w_O=np.append(array_w_O, w_i_O)
        array_w_E=np.append(array_w_E, w_i_E)
        i+=1

    z_theta=np.unique(np.vstack((z_O_theta,z_E_theta)), axis=0)
    array_w=np.union1d(array_w_O, array_w_E)

    I_0=np.mean(z_theta, axis=0)

    IWAE_O=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w_O,z_O_theta)]), axis=0)/np.sum(array_w_O)
    IWAE_E=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w_E,z_E_theta)]), axis=0)/np.sum(array_w_E)
    IWAE_OUE=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w,z_theta)]), axis=0)/np.sum(array_w)

    delta_K=IWAE_OUE-0.5*(IWAE_O+IWAE_E)

    SS=I_0+delta_K/geom.pmf(K, p=r)

    return SS

#### ML-RR
    
def estimateur_ML_RR_gradientlogvraisemblance(x, theta, A, b, r):
    K=np.random.geometric(p=0.6, size=1)[0]
    k=0
    array_delta_k=np.array([])
    array_proba_K_sup_k=np.array([])

    while k<K:

        z_O_theta=np.array([])
        z_E_theta=np.array([])

        array_w=np.array([])
        array_w_O=np.array([])
        array_w_E=np.array([])

        i=0
        while i<2**K:

            z_i_O=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]
            z_i_E=simulate_gaussian_vector(mu=np.matmul(A,x)+b, sigma=(2/3)*np.identity(20))[0]

            w_i_E=w(z=z_i_E, x=x, theta=theta, A=A,b=b)
            w_i_O=w(z=z_i_O, x=x, theta=theta, A=A,b=b)

            if i==0:
                z_O_theta=np.append(z_O_theta, z_i_O-theta)
                z_E_theta=np.append(z_E_theta, z_i_E-theta)

            else:
                z_O_theta= np.vstack((z_O_theta, z_i_O-theta))
                z_E_theta= np.vstack((z_E_theta, z_i_E-theta))

            array_w_O=np.append(array_w_O, w_i_O)
            array_w_E=np.append(array_w_E, w_i_E)
            i+=1


        z_theta=np.unique(np.vstack((z_O_theta,z_E_theta)), axis=0)

        array_w=np.union1d(array_w_O, array_w_E)

        I_0=np.mean(z_theta, axis=0)

        IWAE_O=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w_O,z_O_theta)]), axis=0)/np.sum(array_w_O)
        IWAE_E=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w_E,z_E_theta)]), axis=0)/np.sum(array_w_E)
        IWAE_OUE=np.sum(np.array([w_i*z_i for (w_i,z_i) in zip(array_w,z_theta)]), axis=0)/np.sum(array_w)

        delta_k=IWAE_OUE-0.5*(IWAE_O+IWAE_E)

        if k==0:
            proba_k=1
            array_delta_k=np.append(array_delta_k, delta_k)
        else:
            proba_k=geom.cdf(k, p=r)
            array_delta_k=np.vstack((array_delta_k, delta_k))

        array_proba_K_sup_k=np.append(array_proba_K_sup_k, proba_k)

        k+=1
    
    I_0=np.mean(z_theta, axis=0)

    RR=I_0+np.sum(np.array([array_delta_k[i]/array_proba_K_sup_k[i] for i in range(len(array_proba_K_sup_k))]), axis=0)

    return RR