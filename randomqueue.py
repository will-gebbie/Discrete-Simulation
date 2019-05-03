import simpy
import statistics
import numpy as np

server_name = "Jamba Juice" #variable never called; implementation to come in future versions
server_cap = 1 #capacity
entity_name = "Customer"
exp_mean = 5
ia_times = np.random.exponential(exp_mean, size=100)
service_times = np.random.uniform(1, 5, size=100)

#End input data collection

#initialize env for sim
q_env = simpy.Environment()

#resource initialize
q_res = simpy.Resource(q_env, capacity=server_cap)

#Storing variables of each state into arrays
waiting_times = []
queue_lengths = []
start_times = []
end_times = []

def customer(env, name, resource, arrival_time, service_time):
    
    yield env.timeout(arrival_time)

    print('{} arriving at: {}'.format(name, env.now))

    with resource.request() as request:
        yield request
        start_time = env.now

        #calculate waiting time
        waiting_time = env.now - arrival_time
        print('{} waiting time is: {}'.format(name, waiting_time))
        
        #start and end service
        print('{} starting service at: {}'.format(name, env.now))
        print('Starting Queue Length : {}'.format(len(resource.queue)))
        start_len = len(resource.queue)

        yield q_env.timeout(service_time)

        end_time = env.now

        print('{} leaving at: {}'.format(name, env.now))
        print('Ending Queue Length: {}'.format(len(resource.queue)))
        end_len = len(resource.queue)


        #add to info to arrays
        waiting_times.append(waiting_time)
        queue_lengths.append(start_len)
        queue_lengths.append(end_len)
        end_times.append(end_time)
        start_times.append(start_time)

def idleTime(start_arr, end_arr):
    total_idle = 0

    for i in range(len(start_arr) - 1):
        total_idle += (start_arr[i+1] - end_arr[i])
    return total_idle

def resourceUtil(total_idle, total_time):
    busy_time = total_time - total_idle
    ratio = busy_time/total_time
    percent = ratio * 100
    return percent

#start at time 0
arrival_time = 0

#number of entities
total_entities = len(ia_times)

#start simulation (main routine)
for i in range(total_entities):
    arrival_time += ia_times[i]
    service_time = service_times[i]
    q_env.process(customer(q_env, (entity_name + ' {}'.format(i+1)), q_res, arrival_time, service_time)) 

q_env.run()

#Confidence Interval Calculation
std_dev_wt = np.std(waiting_times)
wt_mean = np.mean(waiting_times)
zscore = 1.96

durationoffset = (zscore * std_dev_wt)/np.sqrt(total_entities)

ciwt = [wt_mean - durationoffset, wt_mean + durationoffset]

#Output
print("100 Entities\n")
print('Minimum Queue Length = {} {}s'.format(min(queue_lengths), entity_name))
print('Maximum Queue Length = {} {}s'.format(max(queue_lengths), entity_name))
print('Total Idle Time = {} minutes'.format(idleTime(start_times, end_times)))
print('Resource Utilization Percent = {} %'.format(resourceUtil(idleTime(start_times, end_times), end_times[-1])))
print('Total Queue Time = {} minutes'.format(sum(waiting_times)))
print('Mean Waiting Time = {} minutes'.format(statistics.mean(waiting_times)))
print('Variance of Waiting Time = {} minutes\n'.format(statistics.variance(waiting_times)))

print("95% Confidence Interval: [{}, {}]".format(ciwt[0], ciwt[1]))
