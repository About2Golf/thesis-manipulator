
import math as m

# import numpy as np
# a = np.array([1,0,0])
# b = np.array([0,1,0])
# #print the result
# print(np.cross(a,b))

p = [3, 1, -2, 1]
q = [2, -1, 2, 3]

def sub(A, B):
    return [a - b for a, b in zip(A, B)]

def add(A, B):
    return [a + b for a, b in zip(A, B)]

def mag(x):
    # https://stackoverflow.com/questions/9171158/how-do-you-get-the-magnitude-of-a-vector-in-numpy
    return m.sqrt(sum(i**2 for i in x))

def cross(a, b):
    # https://stackoverflow.com/questions/1984799/cross-product-of-two-vectors-in-python
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c

def dot(a, b):
    # https://stackoverflow.com/questions/35208160/dot-product-in-python-without-numpy
    return sum(x*y for x,y in zip(a,b))

def quatmultiply(p,q):
    scalar = p[0]*q[0] - dot(p[1::],q[1::])
    vi = p[0]*q[1] + q[0]*p[1] + cross(p[1::],q[1::])[0]
    vj = p[0]*q[2] + q[0]*p[2] + cross(p[1::],q[1::])[1]
    vk = p[0]*q[3] + q[0]*p[3] + cross(p[1::],q[1::])[2]
    return [scalar, vi, vj, vk]

def make_quat(vector):
    return [0, vector[0], vector[1], vector[2]]

print(cross(p[1::],q[1::]))
print(dot(p[1::],q[1::]))
print(quatmultiply(quatmultiply(p,q),q))

# def calc_rotation(rotation, deg):
#     rad = deg*m.pi/180
#     if rotation == "PITCH":
#         q = [m.cos(rad/2), unitx[0]*m.sin(rad/2), unitx[1]*m.sin(rad/2), unitx[2]*m.sin(rad/2)]
#         q_star = [m.cos(rad/2), -unitx[0]*m.sin(rad/2), -unitx[1]*m.sin(rad/2), -unitx[2]*m.sin(rad/2)]
#     else:
#         q = [m.cos(rad/2), unitz[0]*m.sin(rad/2), unitz[1]*m.sin(rad/2), unitz[2]*m.sin(rad/2)]
#         q_star = [m.cos(rad/2), -unitz[0]*m.sin(rad/2), -unitz[1]*m.sin(rad/2), -unitz[2]*m.sin(rad/2)]
#     r_bot1_prime = quatmultiply(quatmultiply(q,r_bot1),q_star)
#     r_bot2_prime = quatmultiply(quatmultiply(q,r_bot2),q_star)
#     r_bot3_prime = quatmultiply(quatmultiply(q,r_bot3),q_star)
#     r_top4_prime = quatmultiply(quatmultiply(q,r_top4),q_star)
#     r_top5_prime = quatmultiply(quatmultiply(q,r_top5),q_star)
#     r_top6_prime = quatmultiply(quatmultiply(q,r_top6),q_star)
#     bot_mirror_norm = cross(r_bot1_prime[1:3]-r_bot2_prime[1:3],r_bot3_prime[1:3]-r_bot2_prime[1:3]);
#     top_mirror_norm = cross(r_top4_prime[1:3]-r_top5_prime[1:3],r_top6_prime[1:3]-r_top5_prime[1:3]);
#     bot_mirror_norm = bot_mirror_norm/mag(bot_mirror_norm);
#     top_mirror_norm = top_mirror_norm/mag(top_mirror_norm);
#     top_ints_pt = calc_beam_refl(top_mirror_norm,beam1[1:3],beam2[1:3],r_top4_prime[1:3])
#
# unitx = [1,0,0]
# unity = [0,1,0]
# unitz = [0,0,1]
# l_focus = 10.823   # mm
#
# r_bot1 = [0, -12.7, 20.882, 2.312]
# r_bot2 = [0, 0, 11.901, -6.669]
# r_bot3 = [0, 12.7, 20.882, 2.312]
# r_top4 = [0, -25.4, 23.324, 37.204]
# r_top5 = [0, 0, 5.364, 19.244]
# r_top6 = [0, 25.4, 23.324, 37.204]
# beam1 = [0, 0, 80, 32.45]
# beam2 = [0, 0, 18.57, 32.45]
#
# r_bot1_prime = [0, 0, 0, 0]
# r_bot2_prime = [0, 0, 0, 0]
# r_bot3_prime = [0, 0, 0, 0]
# r_top4_prime = [0, 0, 0, 0]
# r_top5_prime = [0, 0, 0, 0]
# r_top6_prime = [0, 0, 0, 0]
