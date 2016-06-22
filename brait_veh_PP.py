# -*- coding: utf-8 -*-
"""
Created on Tue May 24 10:23:22 2016

@author: mb540
"""

import numpy as np
import matplotlib.pyplot as plt

dt = .01
T = 1000
iterations = int(T/dt)

### agent ###
radius = 2
sensors_angle = np.pi/3                     # angle between sensor and central body line
length_dir = 3

pos_centre = np.zeros((2,1))                       # centre of mass
vel = np.zeros((2,1))
theta = 0

max_speed = 1

# sensors
sensors_n = 2
motors_n = 2
variables = sensors_n + motors_n
sensor = np.zeros((sensors_n,))

temp_orders = 1

# perceptual inference
rho = np.zeros((variables,temp_orders))

mu_x = np.zeros((variables,temp_orders))
mu_d = np.array([[2],[2]])

eps_z = np.zeros((variables,temp_orders))
eps_w = np.zeros((motors_n,temp_orders))
eps_w2 = np.zeros((sensors_n,temp_orders))
xi_z = np.zeros((variables,temp_orders))
xi_w = np.zeros((motors_n,temp_orders))
xi_w2 = np.zeros((sensors_n,temp_orders))
pi_z = 10*np.ones((variables,temp_orders))
pi_z[sensors_n:variables,0] *= 1
pi_w = 10*np.ones((motors_n,temp_orders))
pi_w2 = .0000000000012000*np.ones((sensors_n,temp_orders))
sigma_z = 1/(np.sqrt(pi_z))
sigma_w = 1/(np.sqrt(pi_w))
sigma_w2 = np.zeros((2,1))#1/(np.sqrt(pi_w2))

FE = np.zeros((iterations,))

# active inference
a = np.zeros((motors_n,temp_orders))

# noise
z = np.zeros((variables,iterations))
z[0,:] = sigma_z[0,0]*np.random.randn(1,iterations)
z[1,:] = sigma_z[1,0]*np.random.randn(1,iterations)
z[2,:] = sigma_z[2,0]*np.random.randn(1,iterations)
z[3,:] = sigma_z[3,0]*np.random.randn(1,iterations)


# fluctuations
w = np.zeros((motors_n,iterations))
w[0,:] = sigma_w[0,0]*np.random.randn(1,iterations)
w[1,:] = sigma_w[1,0]*np.random.randn(1,iterations)

w2 = np.zeros((sensors_n,iterations))
w2[0,:] = sigma_w2[0,0]*np.random.randn(1,iterations)
w2[1,:] = sigma_w2[1,0]*np.random.randn(1,iterations)

# data (history)
pos_centre_history = np.zeros((2,iterations))
vel_centre_history = np.zeros((1,iterations))
vel_history = np.zeros((2,iterations))
theta_history = np.zeros((1,iterations))
orientation_history = np.zeros((2,2,iterations))
sensor_history = np.zeros((sensors_n,iterations))
rho_history = np.zeros((variables,iterations))                  # noisy version of the sensors

mu_x_history = np.zeros((iterations,variables,temp_orders))
mu_d_history = np.zeros((iterations,sensors_n,temp_orders))
a_history = np.zeros((iterations,motors_n))

### environment ###

# light source
pos_centre_light = np.array([[39.],[47.]])
light_intensity = 200

def light_level(point):
    distance = np.linalg.norm(pos_centre_light - point)
    return light_intensity/(distance**2)
    
def f(sensed_value):
    # vehicles 2
    return np.tanh(sensed_value)
    
    # vehicles 3
    # return .5*(1-np.tanh(sensed_value))
    
def s(sensed_value):
    # vehicles 3
    return 1/(1+np.exp(-sensed_value))
    
def dsdmu_x(sensed_value):
    return s(sensed_value)*(1-s(sensed_value))
    
def dsda(sensed_value):
    return s(sensed_value)*(1-s(sensed_value))

def dfdmu_x(sensed_value):
    # vehicles 2
    return (1 - np.tanh(sensed_value)**2)

    # vehicles 3
#    return .5*(np.tanh(sensed_value)**2)


### plot ###

# plot initial position
plt.close('all')
#fig = plt.figure(0)
#    
#plt.plot(pos_centre_light[0], pos_centre_light[1], color='orange', marker='o', markersize=20)
#
#orientation_endpoint = pos_centre + length_dir*(np.array([[np.cos(theta)], [np.sin(theta)]]))
#orientation = np.concatenate((pos_centre,orientation_endpoint), axis=1)                            # vector containing centre of mass and endpoint for the line representing the orientation
#
#plt.xlim((0,100))
#plt.ylim((0,100))
#
## update the plot thrpugh objects
#ax = fig.add_subplot(111)
#line1, = ax.plot(pos_centre[0], pos_centre[1], color='lightblue', marker='.', markersize=30*radius)       # Returns a tuple of line objects, thus the comma
#line2, = ax.plot(orientation[0,:], orientation[1,:], color='black', linewidth=2)            # Returns a tuple of line objects, thus the comma


### initialise variables ###
pos_centre = np.array([[47.],[55.]])            # can't start too close or too far for some reason
pos_centre = 100*np.random.random((2,1))
pos_centre = np.array([[67.],[85.]])
#pos_centre = 5*np.random.standard_normal((2,1))+pos_centre_light

#vel = 2*np.random.random((2,1))-1

omega = 0
theta = np.pi*2*np.random.uniform()
#theta = 4*np.pi/3
#theta =np.pi/3

eta_mu_x = 1*np.ones((variables,temp_orders))
eta_a = 10*np.ones((motors_n,1))

sensor1_pos_history = np.zeros((2,iterations))
sensor2_pos_history = np.zeros((2,iterations))

for i in range(iterations-1):
    print(i)
    
    # perception
    sensor[0] = light_level(pos_centre + radius*(np.array([[np.cos(theta+sensors_angle)], [np.sin(theta+sensors_angle)]])))            # left sensor
    sensor[1] = light_level(pos_centre + radius*(np.array([[np.cos(theta-sensors_angle)], [np.sin(theta-sensors_angle)]])))            # right sensor
    
    sensor += + z[0:sensors_n,i]
    
    # action
#    vel[0] = x[i,0,1]                   # attach neuron to motor
#    vel[1] = x[i,1,1]                   # attach neuron to motor
    
    # vehicle 2
#    vel[0] =  f(a[1])                   # attach neuron to motor
#    vel[1] =  f(a[0])                   # attach neuron to motor
    
    # vehicle 3
    vel[0] = max_speed*(1-s(a[0]))                   # attach neuron to motor
    vel[1] = max_speed*(1-s(a[1]))                   # attach neuron to motor
    
    vel[:,0] += + z[sensors_n:variables,i]
    
    # translation
    vel_centre = (vel[0]+vel[1])/2
    pos_centre += dt*(vel_centre*np.array([[np.cos(theta)], [np.sin(theta)]]))
    
    # rotation
    omega = 50*np.float((vel[1]-vel[0])/(2*radius))
    theta += dt*omega
    
    ### inference ###
    
    # add noise and fluctuations
    rho[0:sensors_n,0] = sensor                                     # rho[0]: left sensor, rho[1]: right sensor
    rho[sensors_n:variables,0] = np.squeeze(vel)                    # rho[2]: left sensor, rho[3]: right motor

    eps_z[:,0] = np.squeeze(rho - mu_x)
    xi_z[:,0] = pi_z[:,0]*eps_z[:,0]
        
#    eps_w[0,0] = mu_x[sensors_n,0] - f(mu_x[1,0])                  # vehicle 2b
#    eps_w[1,0] = mu_x[sensors_n+1,0] - f(mu_x[0,0])                # vehicle 2b
    eps_w[0,0] = mu_x[sensors_n,0] - max_speed*(1 - s(mu_x[0,0]))             # vehicle 3a
    eps_w[1,0] = mu_x[sensors_n+1,0] - max_speed*(1 - s(mu_x[1,0]))           # vehicle 3a
    xi_w[:,0] = pi_w[:,0]*eps_w[:,0]
    
    eps_w2[:,0] = mu_x[0:sensors_n,0] - mu_d[:,0]
    xi_w2[:,0] = pi_w2[:,0]*eps_w2[:,0]
    
    FE[i] = .5*(np.trace(np.dot(eps_z,np.transpose(xi_z))) + np.trace(np.dot(eps_w,np.transpose(xi_w))) + np.trace(np.dot(eps_w2,np.transpose(xi_w2))))
    
    # perception
#    dFdmu_x = np.transpose(np.array([xi_z[:,0]*-1 + np.concatenate([np.flipud(xi_w[:,0])*-dfdmu_x(mu_x[0:sensors_n,0]) + xi_w2[:,0], xi_w[:,0]])]))     # vehicle 2b
    dFdmu_x = np.transpose(np.array([xi_z[:,0]*-1 + np.concatenate([xi_w[:,0]*max_speed*dsdmu_x(mu_x[0:sensors_n,0]) + xi_w2[:,0], xi_w[:,0]])]))               # vehicle 3a
    mu_x += dt* -eta_mu_x*dFdmu_x
    
    # action
#    dFda = np.transpose(np.array([np.flipud(xi_z[sensors_n:variables,0])*(1-np.tanh(a[:,0])**2)]))              # vehicle 2b
    dFda = np.transpose(np.array([xi_z[sensors_n:variables,0]*-max_speed*dsda(a[:,0])]))                                 # vehicle 3a
    a += dt* -eta_a*dFda
    
    # update plot
#    if np.mod(i,200)==0:                                                                    # don't update at each time step, too computationally expensive
#        orientation_endpoint = pos_centre + length_dir*(np.array([[np.cos(theta)], [np.sin(theta)]]))
#        orientation = np.concatenate((pos_centre,orientation_endpoint), axis=1)
#        line1.set_xdata(pos_centre[0])
#        line1.set_ydata(pos_centre[1])
#        line2.set_xdata(orientation[0,:])
#        line2.set_ydata(orientation[1,:])
#        fig.canvas.draw()
    #input("\nPress Enter to continue.")                                                    # adds a pause

    # save data
    vel_centre_history[0,i] = vel_centre
    pos_centre_history[:,i] = pos_centre[:,0]
    vel_history[:,i] = vel[:,0]
    theta_history[:,i] = theta    
    sensor_history[:,i] = sensor[:]
    rho_history[:,i] = np.squeeze(rho[:])
    
    mu_x_history[i,:,:] = mu_x
    mu_d_history[i,:,:] = mu_d
    a_history[i,:] = a[:,0]
    
plt.figure(1)
plt.plot(pos_centre_history[0,:-1], pos_centre_history[1,:-1])
plt.xlim((0,100))
plt.ylim((0,100))
plt.plot(pos_centre_light[0], pos_centre_light[1], color='orange', marker='o', markersize=20)
plt.plot(pos_centre_history[0,0], pos_centre_history[1,0], color='red', marker='o', markersize=8)

plt.figure(2)
plt.subplot(1,2,1)
plt.plot(range(iterations), rho_history[0,:], 'b', range(iterations), mu_x_history[:,0,0], 'r')
plt.title("Inferred light level")
plt.subplot(1,2,2)
plt.plot(range(iterations), rho_history[1,:], 'b', range(iterations), mu_x_history[:,1,0], 'r')


plt.figure(3)
plt.subplot(1,2,1)
plt.plot(range(iterations), vel_history[0,:], 'b', range(iterations), mu_x_history[:,2,0], 'r')
plt.title("Inferred speed")
plt.subplot(1,2,2)
plt.plot(range(iterations), vel_history[1,:], 'b', range(iterations), mu_x_history[:,3,0], 'r')


plt.figure(4)
plt.subplot(1,2,1)
plt.plot(range(iterations), a_history[:,0])
plt.title("Actions")
plt.subplot(1,2,2)
plt.plot(range(iterations), a_history[:,1])


#plt.figure(5)
#plt.subplot(1,2,1)
#plt.plot(range(iterations), mu_x_history[:,0,0], 'b', range(iterations), mu_d_history[:,0,0], 'r')
#plt.title("Priors")
#plt.subplot(1,2,2)
#plt.plot(range(iterations), mu_x_history[:,1,0], 'b', range(iterations), mu_d_history[:,1,0], 'r')

plt.figure(6)
plt.plot(range(iterations), FE)
plt.title("Free energy")

#plt.figure(7)
#data = np.zeros((100,100))
#for i in range(100):
#    for j in range(100):
#        data[i,j] = light_level(np.array([i,j])) + sigma_z[0,0]*np.random.randn()
#plt.imshow(data, vmin=0, origin='lower')#, vmax=10)
#plt.colorbar()
#
#plt.show()