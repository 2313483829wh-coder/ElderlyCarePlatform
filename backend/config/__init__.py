# 使用 PyMySQL 替代 mysqlclient（无需编译，Docker 构建更快）
# 本地默认 sqlite 开发环境不一定会安装 PyMySQL，因此这里做兼容处理。
try:
    import pymysql
except ImportError:
    pymysql = None

if pymysql is not None:
    pymysql.install_as_MySQLdb()

# Improve local sqlite concurrency without affecting MySQL deployments.
from . import sqlite_compat  # noqa: F401,E402
