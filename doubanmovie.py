# -*- coding: utf-8 -*-
"""
Created on Tue May 16 21:44:43 2017

@author: crd
"""

# -*- coding: utf-8 -*-
import urllib2
import re
from bs4 import BeautifulSoup
import time
import random


class spider():
    '''
    获取网页源代码并将其转化为BeautifulSoup对象
    '''
    def __init__(self,url):
        self.url = url
        self.src_url = 'https://movie.douban.com/'
        self.user_engent = 'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0'
    
    def get_bs(self):
        time.sleep(random.randint(0,10)/8.0)
        req = urllib2.Request(self.url)
        req.add_header('Referer',self.src_url)
        req.add_header('User-Agent', self.user_engent)
        response = urllib2.urlopen(req)
        html = response.read()
        return BeautifulSoup(html,'lxml')


class actor_init_by_name():
    '''
    根据姓名查找演员主页
    '''
    
    def __init__(self,name):
        self.name=name
        #print name
    
    def find_personal_page(self):
        personal_page_url='https://movie.douban.com/subject_search?search_text='+self.name+'&cat=1002'
        #print personal_page_url
        personal_page=spider(personal_page_url)
        personal_page_bs=personal_page.get_bs()
        result_item=personal_page_bs.find(attrs={'class':'result-item'})
        result_item=str(result_item)
        #print result_item
        #<a href="https://movie.douban.com/celebrity/(.*?)</a>
        '''      
        if result_item.find(self.name)==-1:
            raise Exception("Not find the actor")
        
        如果没有查找到对应的演员，则抛出一个错误
        '''
        prefix='https://movie.douban.com/celebrity/'
        index=result_item.find(prefix)+len(prefix)
        self.id=result_item[index:index+7]
        return 'https://movie.douban.com/celebrity/'+str(self.id)+'/'
    
    def find_personal_id(self):
        return self.id
    
    def find_personal_info(self):
        personal_url='https://movie.douban.com/celebrity/'+str(self.id)+'/'
        personal_url_bs=spider(personal_url).get_bs()
        result_item=personal_url_bs.find(attrs={'id':'headline'})
        #删除掉html'<>'里面的代码
        result_item=re.compile('\<.*?\>' ).sub('',str(result_item))
        result_item=str(result_item[result_item.find('性别'):])
        self.info=result_item
        #self.info=result_item.split('       ')
        #key_list=[]
        #value_list=[]     
        return self.info
    
    def find_personal_works(self):
        '''
         <span class="count">(共29条)</span>
         根据这个写！
        '''
        works_url='https://movie.douban.com/celebrity/'+self.id+'/movies?start=0&format=pic&sortby=vote&'
        works_url_spider=spider(works_url)
        works_url_spider_bs=works_url_spider.get_bs()
        result_item=str(works_url_spider_bs.find_all("span", "count",1))
        result_item=result_item.decode("unicode_escape")
        beg=result_item.find('共')
        end=result_item.find('条')
        result_item=result_item[beg+1:end]
        #print result_item
        self.works_count=int(result_item)
        return self.works_count
    
    def get_works_count():
        return self.works_count


class actor_movie_list():
    '''
    在查找到演员的个人主页并获得作品作品总数后，查找作品及评分
    '''
    
    def __init__(self,actor_id,works_count):
        self.actor_id=actor_id
        self.works_count=works_count
        self.page_list=[]
        self.offset=0
        self.start_url='https://movie.douban.com/celebrity/'+str(self.actor_id)+'/movies?start='+str(self.offset)+'&format=pic&sortby=vote&'
    
    def get_all_movie_page(self):
        while(self.works_count>=(self.offset/10+1)*9):
            new_url='https://movie.douban.com/celebrity/'+str(self.actor_id)+'/movies?start='+str(self.offset)+'&format=pic&sortby=vote&'
            self.page_list.append(new_url)
            self.offset+=10
        #print 'self.page_list='
        #print self.page_list
        return self.page_list
    
    def get_score_in_one_page(self,url):
        '''
        查找一页的作品
        '''
        page_content=spider(url)
        page_bs=page_content.get_bs()
        #print page_bs
        result=str(page_bs.find_all("a", class_="nbg")).decode("unicode_escape")
        result=re.findall('img alt="(.*?)"',result)
        name_list_one_page=str(result).decode("unicode_escape")
        name_list_one_page=name_list_one_page[1:len(name_list_one_page)-1]
        name_list_one_page=name_list_one_page.split(",")
        result=str(page_bs.find_all("div", class_="star clearfix")).decode("unicode_escape")
        result=re.compile('\<.*?\>' ).sub('',str(result))
        result=str(result)
        new_str=','
        for i in result:
            if i in '0123456789./,':
                new_str+=i
        score_list_one_page=re.findall(',(.*?)/',new_str)
        #print type(name_list_one_page)
        #print type(score_list_one_page)
        return name_list_one_page,score_list_one_page
        #score=dict(zip(name_list_one_page,score_list_one_page))
        #print name_list_one_page
        #print str(result.split(",")).decode("utf-8")
    
    def get_all_movie_and_score(self):
        '''
        查找所有页的作品
        '''
        self.get_all_movie_page()
        self.movie_list=[]
        self.score_list=[]
        for item in self.page_list:
            name_in_one_page,score_in_one_page=self.get_score_in_one_page(item)
            self.movie_list.extend(name_in_one_page)
            self.score_list.extend(score_in_one_page)
        append_count=len(self.movie_list)-len(self.score_list)
        for i in range(append_count):
            self.score_list.append('null')
        self.movie_list=str(self.movie_list).decode("unicode_escape")[1:-1]
        self.movie_list.replace('\"','')
        self.movie_list.replace("\'",'') 
        #self.movie_list=self.movie_list.split(',')
        return self.movie_list,self.score_list        


class actor_spider():
    '''
    将上面两个类组合起来即可
    '''
    
    def __init__(self,name):
        self.name=name
        actor=actor_init_by_name(name)
        actor.find_personal_page()
        self.id=actor.find_personal_id()
        self.info=actor.find_personal_info()
        self.works_count=actor.find_personal_works()
        movie_list=actor_movie_list(self.id,self.works_count)
        movie_list.get_all_movie_page()
        self.movie_list,self.score_list=movie_list.get_all_movie_and_score()
        
    def get_info(self):
        res='姓名:'+'\n        '+self.name+'\n\n\n'
        res+='ID:'+'\n        '+self.id+'\n\n\n'
        res+=str(self.info)
        res+='作品及评分:\n        '+self.movie_list+'\n        '+str(self.score_list)
        res+='\n\n'
        res+='#'*50
        res+='\n\n'
        return res


class txt_io():
    
    def __init__(self,inputpath,outputpath):
        '''
        inputpath：输入文件路径，这个文件记录需要爬取得的演员的姓名，用换行符隔开
        outputpath：输出文件的路径
        '''
        self.inputpath=inputpath
        self.outputpath=outputpath
        self.inputtxt=open(inputpath)
        self.outputtxt=open(outputpath, 'wb')
    
    def write(self):
        for line in self.inputtxt:
            line=line.strip()
            #print line
            '''
            tmp=actor_spider(line)
            self.info=tmp.get_info()
            #print self.info
            self.outputtxt.write(self.info)
            '''
            try:
                tmp=actor_spider(line)
                self.info=tmp.get_info()
                #print self.info
                self.outputtxt.write(self.info)
            except:
                self.outputtxt.write('\n'+line+'\n'+'Not found\n\n'+'#'*50+'\n\n')
            
        self.inputtxt.close()
        self.outputtxt.close()
            
                
        
if __name__ == '__main__':
    #shiyan = spider('http://www.douban.com')
    #print shiyan.get_bs()
    t=txt_io('/home/crd/桌面/doubanmovie_spider/in.txt','/home/crd/桌面/doubanmovie_spider/out.txt')
    t.write()

