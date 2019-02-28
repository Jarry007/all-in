# all-in
python-flask博客系统

## 预览地址 [blogai.cn](https://blogai.cn)


该项目使用mysql,所以   
	`SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')` 中的 `DATABASE_URL` 的格式为:   
	数据库+数据库驱动://数据库账号:数据库密码@数据库地址:端口/数据库名  
	例如：` mysql+pymysql://root:123456@127.0.0.1:3306/demo`
 