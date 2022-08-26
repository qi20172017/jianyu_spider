import redis
from model.db_connects import RDS_PASSWORD, RDS_DB, RDS_PORT, RDS_HOST

pool_100_2 = redis.ConnectionPool(host=RDS_HOST, port=RDS_PORT, db=RDS_DB, password=RDS_PASSWORD)
rds_100_2 = redis.StrictRedis(connection_pool=pool_100_2)

pool_local_1 = redis.ConnectionPool(host="127.0.0.1", port=6379)
rds_local_1 = redis.StrictRedis(connection_pool=pool_local_1)

