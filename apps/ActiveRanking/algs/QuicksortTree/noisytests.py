import numpy as np

def getRandomMatrix():
    n = 100
    lamb = 20. #higher lambda = higher noise
    scale = 1.0/lamb
    nqueries = 10000

    arm_mean = np.hstack((0.,np.cumsum(np.random.exponential(scale=scale, size=n-1))))
    W = np.zeros((n,n))
    for _ in range(nqueries):
        i1 = np.random.randint(n)
        i2 = np.random.randint(n)
        while i2==i1:
            i2 = np.random.randint(n)
        if np.random.rand() < 1./(1+np.exp(-(arm_mean[i1]-arm_mean[i2]))):
            W[i1,i2] += 1.
        else:
            W[i2,i1] += 1.
    return W

if __name__ == "__main__":
    W = getRandomMatrix()
