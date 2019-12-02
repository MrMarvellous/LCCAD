# coding=utf-8
from livePredict_func import train,view,visual_back_prop,erasure_new_data,new_data,view_new

def me(val, list=[]):
    list.append(val)
    return list





if __name__ == '__main__':
    # train()
    # view()
    # view_new()
    # visual_back_prop()
    # erasure_new_data()
    # new_data()
    # print('run OK')
    # mylist = me(123,[])
    # print(mylist)
    list = map(lambda x:x+1, range(6))
    for i in list:
        print(i)
    # print('sss')

    pass
