"""Project package initialization."""

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    # mysqlclient can be used instead of PyMySQL in production images.
    pass
