from fdfs_client.client import Fdfs_client


# 创建FastDFS实例对象
client = Fdfs_client('./client.conf')

# 调用FastrDFS客户端上传文件

ret = client.upload_by_filename('/Users/liushiyang/Desktop/01.png')

print(ret)