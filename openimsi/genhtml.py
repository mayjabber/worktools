#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os,sys
import openimsi

HOST_LIST = 'hostlist'
BLACK_LIST = 'blacklist'
SOURCE_DIR = 'src'
DIST_DIR = 'target'
OUT_TYPE = 'xlsx'

def convert(run_dir,src_dir,dist_dir):
    print 'Start convert %s:'%src_dir
    for file_name in os.listdir(src_dir):
        if os.path.isdir(file_name):
            pass
        else:
            name,ext = os.path.splitext(file_name)
            print "convert %s%s"%(name,ext)
            output_file = '%s/%s'%(dist_dir,name)
            result = t.load('%s/%s'%(src_dir, file_name))
            if result:
                if OUT_TYPE == 'html':
                    open(output_file + '.html', 'w').write(t.get_html('all'))
                elif OUT_TYPE == 'xlsx':
                    t.get_xlsx(output_file +'.xlsx')
    print 'Convert %s Complite!\n'%src_dir
    return 0

if __name__ == '__main__':
    #初始化转换器参数
    run_dir = os.path.split(os.path.realpath(__file__))[0]
   
    t = openimsi.Tables()
    host_list = '%s/%s'%(run_dir,HOST_LIST)
    for ext in ('.txt','.xlsx'):
        if os.path.isfile(host_list + ext):
            print "load Host List from %s%s"%(host_list,ext)
            t.hostlist = t.load_list(host_list + ext)
            break
    if t.hostlist == []:
        print 'Please give a useful hostlist file like hostlist.txt or hostlist.xlsx in script dir!'
        sys.exit(1)
    black_list = '%s/%s'%(run_dir,BLACK_LIST)
    for ext in ('.txt','.xlsx'):
        if os.path.isfile(black_list + ext):
            print "load Black List from %s%s"%(black_list,ext)
            t.blacklist = t.load_list(black_list + ext)
            break
    #获得输入输出目录
    for value in os.listdir(run_dir):
        src_dir = "%s/%s"%(run_dir,value)
        if os.path.isdir(src_dir) and value[0] != '.':
            dist_dir = "%s/%s"%(src_dir,DIST_DIR)
            if os.path.isdir(dist_dir):
                print "skip %s"%src_dir
                pass
            else:
                os.mkdir(dist_dir)
                convert(run_dir,src_dir,dist_dir)
    sys.exit(0)

