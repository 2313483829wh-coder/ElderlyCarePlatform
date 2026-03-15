# 使用 PyMySQL 替代 mysqlclient（无需编译，Docker 构建更快）
import pymysql
pymysql.install_as_MySQLdb()
