from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


class Crawler_DC:
    BASE_URL = "https://gall.dcinside.com"
    LIST_URL = "https://gall.dcinside.com/mgallery/board/lists"

    # 헤더 설정
    headers = [{'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}]

    # DB
    contentsDf = pd.DataFrame(columns=["gal", "num", "category", "title", "writer", "date", "views", "recommend", "content"])

    # Max Idx
    max_dict = {
        'jaetae' : 0,
    }

    # DB Max Init
    db_max = contentsDf.groupby('gal')['num'].max()
    for key in max_dict.keys():
        if (key in db_max.keys()):
            max_dict[key] = db_max[key]

    SLEEP_TIME_SECOND = 5

    def getContentsList_DC(self, gal_name, page):
        # 게시글 리스트
        params = {'id' : gal_name, 'page' : page}
        resp = requests.get(self.LIST_URL, params=params, headers=self.headers[0])
        soup = BeautifulSoup(resp.content, 'html.parser')
        contents = soup.find('tbody').find_all('tr')
        
        return contents

    def readContent(self, content):
        content_dict = dict()
        
        # 글 분류
        category = content.find('td', class_='gall_subject').text
        if (category in ('AD', '공지')):
            return content_dict
        
        content_dict["category"] = category
        
        # 글 번호 추출
        num = content.find('td', class_='gall_num').text
        content_dict["num"] = int(num)
        
        # 제목 추출
        title_tag = content.find('a')
        title = title_tag.text
        
        content_dict["title"] = title
        # print(title)
        
        # 글쓴이 추출
        writer_tag = content.find('td', class_='gall_writer ub-writer').find('span', class_='nickname')
        if writer_tag is not None: # None 값이 있으므로 조건문을 통해 회피 
            writer = writer_tag.text
        else:
            writer = None
        
        # 유동이나 고닉이 아닌 글쓴이 옆에 있는 ip 추출 -> 글쓴이 + ip
        ip_tag = content.find('td', class_='gall_writer ub-writer').find('span', class_='ip')
        if ip_tag is not None:  # None 값이 있으므로 조건문을 통해 회피 
            writer += ip_tag.text
            
        content_dict["writer"] = writer
        
        # 날짜 추출 
        date_tag = content.find('td', class_='gall_date')
        date_dict = date_tag.attrs

        if len(date_dict) is 2:
            date = date_dict['title']
        else:
            date = date_tag.text
            
        content_dict["date"] = date
        
        # 조회 수 추출
        views_tag = content.find('td', class_='gall_count')
        views = views_tag.text
        
        content_dict["views"] = views
        
        # 추천 수 추출
        recommend_tag = content.find('td', class_='gall_recommend')
        recommend = recommend_tag.text
        
        content_dict["recommend"] = recommend
        
        # 게시글 내용
        content_resp = requests.get(self.BASE_URL + title_tag["href"], headers=self.headers[0])
        if content_resp.ok:
            content_soup = BeautifulSoup(content_resp.content, 'html.parser')
            content_content = content_soup.find(class_='write_div').text
            content_dict["content"] = content_content
        
        return content_dict

    def execute(self):
        gal_name = 'jaetae'
        contents = self.getContentsList_DC(gal_name, 1)[:10]

        # 한 페이지에 있는 모든 게시물을 긁어오는 코드 
        for content in contents[::-1]:
            idx = content.find('td', class_='gall_num').text
            if (int(idx) <= self.max_dict[gal_name]):
                continue
            self.max_dict[gal_name] = int(idx)
                
            time.sleep(self.SLEEP_TIME_SECOND)
            content_dict = self.readContent(content)
            if (content_dict):
                content_dict['gal'] = gal_name
                self.contentsDf = self.contentsDf.append(content_dict, ignore_index=True)

    def getData(self):
        return self.contentsDf