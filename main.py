import requests,re,json,sys,os,base64
from PIL import Image
from io import BytesIO
import apiutil
s=requests.session()
filepath='face//'
AppID = '1107225542'
AppKey = 'HmoRjLdOvrQe2sFB'
VERSION='0.2'
update_log='''
增加了针对检测引擎繁忙的二次检测队列
增加了故障码输出
'''
max_page=int(input('输入采集页数：'))
face_min_rank=int(input('请输入最低颜值打分（推荐95）：'))
max_age=int(input('请输入最大年龄：'))
def get_cover_id_list(page):
    '''
    输入：页数
    输出：封面id,番号
    返回类型：list
    '''
    raw=s.get('https://www.javbus.cc/page/{0}'.format(page)).text
    filters='''<img src="https://pics.javcdn.pw/thumb/(.*?).jpg" title=".*?">'''
    filters2='''<a class="movie-box" href="https://www.javbus.cc/(.*?)">'''
    cover_id_list=re.findall(filters,raw)
    fid=re.findall(filters2,raw)
    return cover_id_list,fid

def get_cover_content_list(cover_id_list):
    cover_content_list=[]
    for cover_id in cover_id_list:
        cover_content_list.append(s.get('https://pics.javcdn.pw/cover/{0}_b.jpg'.format(cover_id)).content)
    return cover_content_list

def saveimage(image,name):
    try:
        image=Image.open(BytesIO(image))
        image.save(filepath+name+'.jpg')
        return True
    except:
        return False

def saveerrorimage(image,name):
    try:
        image=Image.open(BytesIO(image))
        image.save('error/'+name+'.jpg')
        return True
    except:
        return False

def face_rank(page):
    cover_id_list,name_list=get_cover_id_list(page)
    cover_content_list=get_cover_content_list(cover_id_list)
    for cover_content,name,ids in zip(cover_content_list,name_list,cover_id_list):
        ai_obj = apiutil.AiPlat(AppID, AppKey)
        rsp = ai_obj.face_detectface(cover_content, 0)
        if rsp['ret'] == 0:
            for face in rsp['data']['face_list']:
                if face['beauty'] > face_min_rank and face['gender'] < 50 and face['age'] < max_age:
                    print('{0}颜值通过 分值{1}  年龄{2}'.format(name,face['beauty'],face['age']))
                    saveimage(cover_content,name)
        elif rsp['ret'] == -2147483636:
            print('{0}识别繁忙，重试'.format(name))
            ai_obj = apiutil.AiPlat('1106858595','bNUNgOpY6AeeJjFu')
            rsp = ai_obj.face_detectface(cover_content, 0)
            if rsp['ret'] == 0:
                for face in rsp['data']['face_list']:
                    if face['beauty'] > face_min_rank and face['gender'] < 50 and face['age'] < max_age:
                        print('{0}颜值通过 分值{1}  年龄{2}'.format(name,face['beauty'],face['age']))
                        saveimage(cover_content,name)
            elif rsp['ret'] == -2147483636:
                print('{0}第二次识别失败，放弃识别'.format(name))
                saveerrorimage(cover_content,name)
            else:
                print('{2}识别出错，错误码{0}，错信信息{1}'.format(rsp['ret'],rsp['msg'],name))
        else:
            print('{2}识别出错，错误码{0}，错信信息{1}'.format(rsp['ret'],rsp['msg'],name))


def main():
    for i in range(1,max_page):
        face_rank(i)

if __name__ == '__main__':
    main()