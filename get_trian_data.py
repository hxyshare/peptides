# -*- coding: utf-8 -*-


with open('./data/peaks.db.mgf.train.label','r') as f:
        #不等等于NOI
        #label没有在氨基酸序列里面
        
        tmp =''.join(f.readlines()).strip().split('\n\n')
        
        count = 0
        final_result = []
        for i in tmp:
            print(len(i.strip().split('/n')))