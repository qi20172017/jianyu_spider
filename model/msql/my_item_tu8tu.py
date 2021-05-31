from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP
import datetime
from model.msql.my_moen_db import MyBase, MySESSION
from model.mixin import ModelMixin


class Tu8tu(MyBase, ModelMixin):
    __tablename__ = "tu8tu"

    __key__ = 'item_id'
    __table_args__ = (
        {"schema": "moen"}
    )

    session = MySESSION

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
