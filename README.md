

I. Huong dan chay
Cai Docker

Lan dau tien clone :
'''
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.4
docker run --name es07 --net elastic -p 9200:9200 -it -m 1GB --restart always docker.elastic.co/elasticsearch/elasticsearch:8.11.4

-> thay password, ca vào dòng 6,7 file app.py
'''

Lan sau:
'''
docker start es07
'''

'''
cd api
python app.py
'''

'''
test :
data 
title,                  content,                             title_vector,       content_vector
title01 xuanbao ,       trường đại học công nghệ, , 
title02,                bạn phải đủ 127 tín , , 
title03                 lương IT 100 triệu, , 
title04,                xstk kho vai chuong, , 

question : "toi da hoc 50 tin" -> output : ban phai du 127 tin -> OK
'''