import datetime
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from model.pg.pg_moen_db import PgBase, PgSESSION
from model.mixin import ModelMixin


class PgTu8tu(PgBase, ModelMixin):
    __tablename__ = "tu8tu"
    __db__ = "dragon"
    __key__ = 'item_id'
    __table_args__ = (
        {"schema": "public"}
    )

    session = PgSESSION

    item_id = Column(String, primary_key=True, comment='')
    create_time = Column(TIMESTAMP(precision=0), nullable=True, comment='作品创建时间')

    insert_time = Column(TIMESTAMP(precision=0), nullable=False, default=datetime.datetime.now, comment='记录创建时间')

    update_time = Column(
        TIMESTAMP(precision=0),
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='记录更新时间',
        index=True
    )
    title = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    item_type = Column(String, nullable=True)
    share_url = Column(String, nullable=True)

    collect_num = Column(Integer, nullable=True)
    praise_num = Column(Integer, nullable=True)
    comment_num = Column(Integer, nullable=True)

    content = Column(Text, nullable=True)
    pic_url = Column(Text, nullable=True)
    author_avatar = Column(String, nullable=True)
    author_id = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    long_content = Column(Text, nullable=True)

    area = Column(String, nullable=True)
    product_sum = Column(String, nullable=True)
    house_type = Column(String, nullable=True)
    style = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)
    city_name = Column(String, nullable=True)
    budget = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    stage_name = Column(String, nullable=True)
    router = Column(String, nullable=True)
