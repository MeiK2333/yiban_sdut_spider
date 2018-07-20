# yiban_sdut_spider

Yiban 一键查询

## 安装

```shell
# 创建虚拟环境
$ python3 -m venv venv
$ source venv/bin/activate
# 安装依赖包
(venv)$ pip install -r requirements.txt
...

# 创建表
(venv)$ cd YibanSDUTSpider
(venv)$ python manage.py makemigrations yiban_sdut
(venv)$ python manage.py migrate
# 修改易班的配置(如果不需要易班登录, 则可以忽略此步)
(venv)$ vim yiban_sdut/config.py
...

# 运行
(venv)$ python manage.py runserver
# 浏览器访问 http://127.0.0.1:8000 以查看网站内容
```

## 发布

发布时请修改 ```settings.py``` 内的 ```DEBUG``` 和 ```ALLOWED_HOSTS``` 项

### 使用 ```gunicorn``` 发布

```shell
# gunicorn 直接提供服务, 监听 5000 端口, 开启 8 个工作进程
$ gunicorn run:app -b 0.0.0.0:5000 -w 8
```

### 使用 ```gunicorn``` + ```nginx```

配置服务脚本

```shell
$ cd YibanSDUTSpider
# 请自行修改端口
$ echo 'source ../venv/bin/activate
nohup gunicorn -w 8 -b 127.0.0.1:6666 YibanSDUTSpider.wsgi&' > start.sh
$ echo "lsof -i:6666  | awk '{print \$2}' | xargs kill" > stop.sh
$ echo './stop.sh
./start.sh' > restart.sh
$ chmod +x start.sh
$ chmod +x stop.sh
$ chmod +x restart.sh
$ ./start.sh
```

nginx 配置

```conf
server {
    listen 80;
    server_name you_domain;
    location / {
        # 修改为你选择的端口
        proxy_pass http://127.0.0.1:6666;
    }
    location /static {
        root /path/to/yiban_sdut_spider/YibanSDUTSpider;
    }
}
```

reload nginx

## License

GNU GENERAL PUBLIC LICENSE Version 3

您可以使用此项目中的全部或部分代码, 但作为交换, 您必须同样开源您的项目