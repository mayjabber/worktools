#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os,sys
import glob

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

run_dir = os.path.realpath(module_path())
sys.path.insert(0,run_dir+'/require')
if os.path.isfile(run_dir):
    run_dir = os.path.dirname(run_dir)

import openimis

HOST_LIST = 'hostlist'
BLACK_LIST = 'blacklist'
SOURCE_DIR = 'src'
DIST_DIR = 'target'
OUT_TYPE = 'xlsx'

CARE_LIST = (
        ('日常检查异常统计','开放平台开放平台日常检查异常统计表*.xlsx','分区日常检查异常明细-未备注/未处理'),
        ('开放平台报警系统管理员后续处理跟踪','开放平台开放平台报警系统管理员后续处理跟踪表*.xlsx','未及时回复,昨日新增未回复'),
        ('','开放平台开放平台操作系统定义作业变化情况统计表*.xlsx','昨日Crontab新增'),
            )

def create_report(dist_dir):
    if os.path.isfile(os.path.join(dist_dir,'运维三组openimis报表检查汇总--.html'.decode('utf-8'))):
        return 0
    output = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" CONTENT="text/html; charset=UTF-8"/>
<body>
<p>大家好！</p>
    <p class="MsoNormal" align="left" style="line-height:12.75pt;text-indent:24pt">附件是昨天的openimis报表的汇总，其中有以下问题需要各位系统管理员关注下，其中有些数据可能与openimis未同步，还是请管理员确认一下，以免出错。其中高亮的行是新出现的异常。</p>
    '''
    count = 0
    for (head,fname,tname) in CARE_LIST:
        try:
            filename = glob.glob(os.path.join(dist_dir,fname.decode('utf-8')))[0]
        except IndexError:
            print "Warning: No found %s,skip it in the report."%fname.decode('utf-8')
            filename = None
        if filename:
            if tname == "分区日常检查异常明细-未备注/未处理":
                try:
                    data = int(dist_dir.split('/')[-2])
                except:
                    data = int(dist_dir.split('\\')[-2])
                maxtry = 10
                while maxtry > 0:
                    maxtry -= 1
                    if data%100 == 1:
                        data -= 69
                    else:
                        data -= 1
                    yesterday_dir = os.path.realpath('%s/../../%s/target'%(dist_dir,data))
                    try:
                        yesterfile = glob.glob(os.path.join(yesterday_dir,fname.decode('utf-8')))[0]
                    except IndexError:
                        yesterfile = None
                    if yesterfile:
                        break
                    if maxtry == 0:
                        yesterfile = None
                if yesterfile:
                    import tableDiff
                    table1 = tableDiff.getTables(filename,tname)
                    table2 = tableDiff.getTables(yesterfile,tname)
                    diff_set = tableDiff.genDiffSet(table1,table2)
                    html = tableDiff.table2htmlHighlight(table1,diff_set)
                else:
                    html = openimis.get_html(filename,tname)
            else:
                html = openimis.get_html(filename,tname)
            soup = openimis.BeautifulSoup(html)
            if len(soup.find_all('tr')) > 1:
                count += 1
                if head:
                    output += '%s)%s:<br/>'%(count,head)
                else:
                    output += '%s)'%count
                output += html
            else:
                pass
    with open(os.path.join(dist_dir,'运维三组openimis报表检查汇总--.html'.decode('utf-8')),'w+') as report_file:
        report_file.write(output)
    print "Create mail html file in '%s'"%dist_dir

def convert(src_dir,dist_dir):
    print 'Start convert %s:'%src_dir
    for file_name in os.listdir(src_dir):
        if os.path.isdir("%s/%s"%(src_dir, file_name)):
            pass
        else:
            name,ext = os.path.splitext(file_name)
            print "convert %s%s"%(name,ext)
            output_file = '%s/%s'%(dist_dir,name)
            t.clear()
            result = t.load('%s/%s'%(src_dir, file_name))
            if result:
                if OUT_TYPE == 'html':
                    open(output_file + '.html', 'w').write(t.get_html('all'))

                elif OUT_TYPE == 'xlsx':
                    t.get_xlsx(output_file +'.xlsx')
    print 'Convert %s Complite!\n'%src_dir
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('')
    if sys.argv[1] in ('-h', '--help'):
        print """usage:
    <-d|--diff> NewFile OldFile      find different in NewFile. 
        """
        sys.exit(0)

    #初始化转换器参数
    print run_dir

    if sys.argv[1] in ('-d', '--diff'):
        import tableDiff
        html = tableDiff.openimisDiff(sys.argv[2], sys.argv[3])
        open('%s/diff.html'%run_dir,'w').write(html)
        print 'output to %s/diff.html\n'%run_dir
        sys.exit(0)

    t = openimis.Tables()

    host_list = '%s/%s'%(run_dir,HOST_LIST)
    for ext in ('.txt','.xlsx'):
        if os.path.isfile(host_list + ext):
            print "load Host List from %s%s"%(host_list,ext)
            t.hostlist = t.load_list(host_list + ext)
            break

    if t.hostlist == []:
        print 'Please give a useful hostlist file like hostlist.txt or hostlist.xlsx in script dir!'
        raw_input("Press Enter to Exit. ")
        sys.exit(1)

    black_list = '%s/%s'%(run_dir,BLACK_LIST)
    for ext in ('.txt','.xlsx'):
        if os.path.isfile(black_list + ext):
            print "load Black List from %s%s"%(black_list,ext)
            t.blacklist = t.load_list(black_list + ext)
            break

    #获得输入输出目录
    dirlist = os.listdir(run_dir)
    dirlist.sort()
    for value in dirlist:
        src_dir = os.path.join(run_dir,value)
        if os.path.isdir(src_dir) and value[0] != '.':
            dist_dir = os.path.join(src_dir,DIST_DIR)
            if os.path.isdir(dist_dir):
                print "skip %s"%src_dir
                create_report(dist_dir)
            elif src_dir in sys.path:
                pass
            else:
                print "%s will be convert"%src_dir
                os.mkdir(dist_dir)
                convert(src_dir,dist_dir)
                create_report(dist_dir)

    print 'All dir convert Complite!\n'
    raw_input("Press Enter to Exit. ")

