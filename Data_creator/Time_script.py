import json
import statistics
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import time


from Server.Initial_model_creation import create_model as initiateModel
from Server.Request_handling import main as handleRequest
from Data_creator.dict_creator import createDataSet

# <----- set options below -----> #

createdata = False

first_RSU = 100
first_MSI = 1

last_RSU = 500
last_MSI = 8

step_RSU = 100
n_iterations = 5

image_format = "png"

# <----- set options above -----> #


data_file = "Server/Solution/input_data.json"
json_file = f"saved_image_data/{first_RSU}-{last_RSU}rsu_{first_MSI}-{last_MSI}msi.json"
img_file = f"saved_image_data/{first_RSU}-{last_RSU}rsu_{first_MSI}-{last_MSI}msi_solve_cross.{image_format}"
img_file_2 = f"saved_image_data/{first_RSU}-{last_RSU}rsu_{first_MSI}-{last_MSI}msi_total_cross.{image_format}"
img_file_3 = f"saved_image_data/{first_RSU}-{last_RSU}rsu_{first_MSI}-{last_MSI}msi_total_init.{image_format}"

range_rsu = range(first_RSU,last_RSU+1,step_RSU)
range_msi = range(first_MSI,last_MSI+1)





def getTimingData(range_rsu,range_msi,n_iterations):

  request = {
    "request_cross": { "type" : "add",
      "legend_requests": [
      "X[RSU_A684_L_8_0,1]"
      ]
    }
  }

  init_times = {}
  handle_times = {}
  handle_times[[key  for key in request.keys()][0]] = {}
  
  for n_rsu in range_rsu:
    init_times[f"RSUs_{n_rsu}"] = {}
    handle_times[[key  for key in request.keys()][0]][f"RSUs_{n_rsu}"] = {}
    for n_msi in range_msi:
      print(f"start {n_rsu} RSU's with {n_msi} MSI's")

      road_layout = createDataSet(n_rsu,n_msi)

      with open(data_file, "w") as outfile:
        json.dump(road_layout, outfile)

      t_init = time.time()
      init_vars = [initiateModel(road_layout) for _ in range(n_iterations)]
      t_mid = time.time()
      handle_vars = [handleRequest(request) for _ in range(n_iterations)]
      t_end = time.time()
      init_times_list = [init_vars[i]["solve_time"] for i in range(n_iterations)]
      handle_times_list = [handle_vars[i]["solve_time"] for i in range(n_iterations)]

      mean_init_time = statistics.mean(init_times_list)
      mean_handle_time = statistics.mean(handle_times_list)

      avg_init_time = (t_mid - t_init) * 1000 / n_iterations
      avg_hangle_time = (t_end - t_mid) * 1000 / n_iterations

      init_times[f"RSUs_{n_rsu}"][f"MSIs_{n_msi}"] = {
        "num_vars": init_vars[0]["num_var"],
        "num_constrs": init_vars[0]["num_constr"],
        "avg_solve_time_ms": mean_init_time,
        "avg_total_time_ms": avg_init_time
        }

      handle_times[[key  for key in request.keys()][0]][f"RSUs_{n_rsu}"][f"MSIs_{n_msi}"] = {
        "num_vars": init_vars[0]["num_var"],
        "num_constrs": init_vars[0]["num_constr"],
        "avg_solve_time_ms": mean_handle_time,
        "avg_total_time_ms": avg_hangle_time
        }

      print(f"finished {n_rsu} RSU's with {n_msi} MSI's")
      print("------------------------------------------")
    
  with open(json_file, "w") as outfile:
    json.dump({"init_times": init_times, "handle_times": handle_times}, outfile)

  return {"init_times": init_times, "handle_times": handle_times}

def createMatrixData(data_dict):
  key = [key for key in data_dict["handle_times"]["request_cross"].keys()]
  value = [value for value in data_dict["handle_times"]["request_cross"][key[0]].keys()]

  nrows = len(value)
  ncols = len(key)
  
  rsu_list = []
  num_vars = np.empty((nrows,ncols),dtype=int)
  num_constrs = np.empty((nrows,ncols),dtype=int)
  avg_time =  np.empty((nrows,ncols))
  avg_total = np.empty((nrows,ncols))

  col = 0
  
  for n_rsu in range(ncols):
    row = 0
    for n_msi in range(nrows):
      myData = data_dict["handle_times"]["request_cross"][key[n_rsu]][value[n_msi]]
      if len(rsu_list) == col:
        rsu_list.append(key[n_rsu].split("_")[1])
      num_vars[row,col] = myData["num_vars"]
      num_constrs[row,col] = myData["num_constrs"]
      avg_time[row,col] = myData["avg_solve_time_ms"]
      avg_total[row,col] = myData["avg_total_time_ms"]
      row += 1
    col += 1

  data_handle = (rsu_list,num_vars,num_constrs,avg_time,avg_total)


  key = [key for key in data_dict["init_times"].keys()]
  value = [value for value in data_dict["init_times"][key[0]].keys()]

  nrows = len(value)
  ncols = len(key)
  
  rsu_list = []
  num_vars = np.empty((nrows,ncols),dtype=int)
  num_constrs = np.empty((nrows,ncols),dtype=int)
  avg_time =  np.empty((nrows,ncols))
  avg_total = np.empty((nrows,ncols))

  col = 0
  for n_rsu in range(ncols):
    row = 0
    for n_msi in range(nrows):
      myData = data_dict["init_times"][key[n_rsu]][value[n_msi]]
      if len(rsu_list) == col:
        rsu_list.append(key[n_rsu].split("_")[1])
      num_vars[row,col] = myData["num_vars"]
      num_constrs[row,col] = myData["num_constrs"]
      avg_time[row,col] = myData["avg_solve_time_ms"]
      avg_total[row,col] = myData["avg_total_time_ms"]
      row += 1
    col += 1

  data_init = (rsu_list,num_vars,num_constrs,avg_time,avg_total)

  return (data_init,data_handle)


def createPlots(data):
  (data_init,data_handle) = data
  (rsu_list,num_vars,num_constrs,avg_time,tot_time) = data_handle
  print(rsu_list)
  legend_data = [f"{i} RSUs" for i in rsu_list]

  fig, axes = plt.subplots(ncols=2)
  fig.set_figwidth(10)
  ax1 = axes[0]
  ax2 = axes[1]
  # ax1.title("Cross request handling")
  ax1.set_xlabel('# variables [-]')
  ax1.set_ylabel('avg. solve time [ms]')

  ax2.set_xlabel('# constraints [-]')
  ax2.set_ylabel('avg. solve time [ms]') 

  ax1.plot(num_vars, avg_time, 'o')
  ax2.plot(num_constrs, avg_time, 'o')
  ax1.legend(legend_data,loc=0) 

  plt.savefig(img_file)

  fig, axes = plt.subplots(ncols=2)
  fig.set_figwidth(10)
  ax1 = axes[0]
  ax2 = axes[1]
  # ax1.title("Cross request handling")
  ax1.set_xlabel('# variables [-]')
  ax1.set_ylabel('total time [ms]')

  ax2.set_xlabel('# constraints [-]')
  ax2.set_ylabel('total time [ms]') 

  ax1.plot(num_vars, tot_time, 'o')
  ax2.plot(num_constrs, tot_time, 'o')
  ax1.legend(legend_data,loc=0) 

  plt.savefig(img_file_2)
  
  (rsu_list,num_vars,num_constrs,avg_time,tot_time) = data_init

  fig, axes = plt.subplots(ncols=2)
  fig.set_figwidth(10)
  ax1 = axes[0]
  ax2 = axes[1]
  # ax1.title("Initial model creation")
  ax1.set_xlabel('# variables [-]')
  ax1.set_ylabel('total time [ms]')

  ax2.set_xlabel('# constraints [-]')
  ax2.set_ylabel('total time [ms]') 

  ax1.plot(num_vars, tot_time, 'o')
  ax2.plot(num_constrs, tot_time, 'o')
  ax1.legend(legend_data,loc=0) 

  plt.savefig(img_file_3)


if __name__ == "__main__":
  if createdata:
    my_data = getTimingData(range_rsu,range_msi,n_iterations)
  else: 
    with open(json_file,'r') as infile:
      my_data = json.load(infile)
  createPlots(createMatrixData(my_data))