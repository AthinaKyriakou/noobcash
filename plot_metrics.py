import pandas as pd
import matplotlib.pyplot as plt
res5=pd.read_csv('results5.txt', sep=" ", header=None, error_bad_lines=False)
res10=pd.read_csv('results10.txt', sep=" ", header=None, error_bad_lines=False)
res5.columns = ["throughput_5", "block_time_5"]
res10.columns = ["throughput", "block_time"]
res5["throughput_10"]=res10['throughput']
res5["block_time_10"]=res10['block_time']
res5["capacity"]=[1,5,10,1,5,10]
#diffculty 4 (first 3 lines)
res5.iloc[:3].plot(x="capacity", y=["throughput_5", "throughput_10"], kind="bar")
f1=plt.figure(1)
plt.title('throughput for dificulty=4')
res5.iloc[:3].plot(x="capacity", y=["block_time_5", "block_time_10"], kind="bar")
f2=plt.figure(2)
plt.title('Block time for dificulty=4')
#difficulty 5 (last 3 lines)
res5.iloc[3:].plot(x="capacity", y=["throughput_5", "throughput_10"], kind="bar")
f3=plt.figure(3)
plt.title('throughput for dificulty=5')
res5.iloc[3:].plot(x="capacity", y=["block_time_5", "block_time_10"], kind="bar")
f4=plt.figure(4)
plt.title('Block time for dificulty=5')
plt.show()