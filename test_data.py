# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from keras.preprocessing import sequence

mass_AA_1 = {
           'A': 71.03711, # 0
           'R': 156.10111, # 1
           'N': 114.04293, # 2
           'D': 115.02694, # 3
           'C': 103.00919, # 4
           'E': 129.04259, # 5
           'Q': 128.05858, # 6
           'G': 57.02146, # 7
           'H': 137.05891, # 8
           'I': 113.08406, # 9
           'L': 113.08406, # 10
           'K': 128.09496, # 11
           'M': 131.04049, # 12
           'F': 147.06841, # 13
           'P': 97.05276, # 14
           'S': 87.03203, # 15
           'T': 101.04768, # 16
           'W': 186.07931, # 17
           'Y': 163.06333, # 18
           'V': 99.06841, # 19
          }
       
index_to_ion = ['NOI', 'y(1+)', 'b(1+)', 'y-NH3(1+)', 'y(2+)', 'y-H2O(1+)', 'b-H2O(1+)',
                'b-NH3(1+)', 'b(2+)', 'y-H2O(2+)', 'b-H2O(2+)', 'y-NH3(2+)', 'b-NH3(2+)', 'y(3+)', 'b(3+)', 'y-H2O(3+)', 'y-NH3(3+)', 'b-H2O(3+)', 'b-NH3(3+)']
ion_to_index = {x:i for  i,x in enumerate(index_to_ion)} 

index_to_mass = ['A','R','N','D','C','E','Q','G','H','I','L','K','M','F','P','S',
                                                            'T','W','Y','V','NOI']
mass_to_index = {x:i for i,x in enumerate(index_to_mass)}

mass_AA_list = list(mass_AA_1.values())

res = {}
#统计粒子
with open('./data/peaks.db.mgf.train.label.100','r') as f:
        #不等等于NOI
        #label没有在氨基酸序列里面
        for line in f.readlines():
            if(len(line.strip())>0):
                 t  = line.strip().split('\t')[1]
                 if t not in res:
                    res[t] = 1
                 else:
                    res[t] += 1

t_res = sorted(res.items(),key = lambda x:x[1],reverse = True)
result = []
for i in range(len(t_res)):
   # print(t_res[i][0])
    result.append(t_res[i][0])
print(result)
data = []


#生成数据
seq_length = 600
tolerance = 0.5
with open('./data/peaks.db.mgf.train.label.100','r') as f:
        #不等等于NOI
        #label没有在氨基酸序列里面
        
        #print(''.join(f.readlines()).split('\n\n')[1].split('\n')[4].split('\t')[-1]) 
        tmp =''.join(f.readlines()).strip().split('\n\n')
        
        count = 0
        final_result = []
        label = []
        #对每一个谱
        for i in tmp:
            #先看一张谱的结果
            one_spectrum_result = []
            print('==='*10)
            if count >= 10:
                break
            temp_fram = pd.DataFrame()
            #每一个谱的每一行数据
            spectrum_label = []
            for j in i.split('\n'):
                a = j.split('\t')
                c={"mass" : [float(a[0])],"ion" : [a[1]],"label":[a[2]]}
                df1 = pd.DataFrame(c)
                tmp_mass_array = np.zeros(21, dtype=int)
                tmp_mass_array[mass_to_index[a[2]]] = 1 
                #print(tmp_mass_array)
                spectrum_label.append(tmp_mass_array)
                temp_fram = pd.concat([temp_fram,df1])
            for j in i.split('\n'):
                #图谱上每一个峰代表的粒子向量。
                ion_list_result = []
                for k in mass_AA_list:
                    new_ion_list = np.zeros(19 ,dtype=int)
                    if (float(j.split('\t')[0])-k)>0:
                        tmpdata = float(j.split('\t')[0])-k
                        #print('tmpdata',tmpdata)
                        #print('k',k)
                        temp_fram.index = temp_fram['mass']
                        left_threshold = tmpdata - tolerance
                        right_threshold = tmpdata + tolerance
                        intervl_data = temp_fram[np.logical_and(temp_fram.index <right_threshold ,temp_fram.index>left_threshold)]
                        if not intervl_data.empty :
                            #看粒子的类型，不是看label的类型
                            tmp_label = intervl_data.iloc[0,0]
                            tmp_index = ion_to_index[tmp_label]
                            new_ion_list[tmp_index] = 1
                            ion_list_result.extend(list(new_ion_list))
                        #如果为周围没有峰怎么办
                        else:
                            ion_list_result.extend(list(np.zeros(19, dtype=int)))
                    else:
                        ion_list_result.extend(list(np.zeros(19, dtype=int)))
                        
                #有的峰可以减的动，有的峰减不动。所以长度不是一样的        
                #print(len(ion_list_result))
                one_spectrum_result.append(ion_list_result)
            #paddding x_train  
            padding_list = np.zeros((seq_length-len(one_spectrum_result),380 ),dtype=int)
            one_spectrum_result_np = np.array(one_spectrum_result)
            f_one_spectrum_result = np.concatenate([one_spectrum_result_np,padding_list],axis=0)
            #print(f_one_spectrum_result.shape)
            final_result.append(list(f_one_spectrum_result))
            
            #padding label 
            padding_label_list = np.zeros((seq_length-len(one_spectrum_result),21 ),dtype=int)
            f_label = np.concatenate([spectrum_label,padding_label_list],axis=0)
            label.append(f_label)
            count += 1 
            #print(len(one_spectrum_result))  
            #print(len(final_result))

            #print(spectrum_label)
            #print(len(spectrum_label))
        print(len(label))
        
        
        
        
                        
                        
                        
                                                