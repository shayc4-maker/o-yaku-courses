import json,numpy as np
K=1000/244.8/48; R5=1.00146
def p5_to_model(x,y): return (((4197.6+(np.asarray(x)-1280)*R5)-4194.98)*K, (2045-np.asarray(y))*K*R5-9.37)
def model_to_p5(X,Z): return (1280+((np.asarray(X)/K+4194.98)-4197.6)/R5, 2045-(np.asarray(Z)+9.37)/(K*R5))
