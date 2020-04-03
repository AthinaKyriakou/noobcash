import pandas as pd
import matplotlib.pyplot as plt
res5=pd.read_csv('results5.txt', sep=" ", header=None, error_bad_lines=False)
res10=pd.read_csv('results10.txt', sep=" ", header=None, error_bad_lines=False)
res5.columns = ["throughput_5", "block_time_5"]
res10.columns = ["throughput", "block_time"]
res5["throughput_10"]=res10['throughput']
res5["block_time_10"]=res10['block_time']
res5["dif_cap"]=[4.1,4.5,4.10,5.1,5.5,5.10]
f1=plt.figure(1)
res5.plot(x="dif_cap", y=["throughput_5", "throughput_10"], kind="bar")
f2=plt.figure(2)
res5.plot(x="dif_cap", y=["block_time_5", "block_time_10"], kind="bar")
plt.show()