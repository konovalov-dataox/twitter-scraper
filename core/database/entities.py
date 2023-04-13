import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey, String, \
    DateTime, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

association_table_project_credentials = Table(
    'assoc_project_cred_notifier', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('credentials_id', Integer, ForeignKey('credentials.id'))
)


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column("project_name", String(100), unique=True)
    rate_limit_tag = Column("rate_limit_tag", String(100))
    error_limit = Column("error_limit", Integer, default=100)
    project_sessions = relationship("ProjectSession",
                                    backref="project",
                                    passive_deletes=True)
    credentials = relationship("Credential",
                               secondary=association_table_project_credentials,
                               back_populates="projects"
                               )


class Credential(Base):
    __tablename__ = 'credentials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cred_type = Column("cred_type", String(100))
    content = Column("content", String(5000))
    projects = relationship('Project',
                            secondary=association_table_project_credentials,
                            back_populates='credentials'
                            )


class ProjectSession(Base):
    __tablename__ = 'project_sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column("session_id", String(50), unique=True,
                        autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="cascade"))
    created_date = Column("created_date", DateTime,
                          default=datetime.datetime.utcnow())
    finished_date = Column("finished_date", DateTime, nullable=True)
    is_active = Column("is_active", Boolean, default=True)


class BenchmarkStatistic(Base):
    __tablename__ = 'benchmark_statistic'
    id = Column(Integer, primary_key=True)
    name = Column("name", String(50))
    node = Column("node", String(100))
    messages = Column("messages", Integer)
    consumers = Column("consumers", Integer)
    memory = Column("memory", Integer)
    messages_ready = Column("messages_ready", Integer)
    message_bytes = Column("message_bytes", Integer)
    messages_ram = Column("messages_ram", Integer)
    reductions = Column("reductions", Integer)
    message_bytes_unacknowledged = Column("message_bytes_unacknowledged",
                                          Integer)
    message_bytes_persistent = Column("message_bytes_persistent", Integer)
    messages_unacknowledged = Column("messages_unacknowledged", Integer)
    message_bytes_ready = Column("message_bytes_ready", Integer)
    messages_unacknowledged_ram = Column("messages_unacknowledged_ram", Integer)
    message_bytes_paged_out = Column("message_bytes_paged_out", Integer)
    messages_ready_ram = Column("messages_ready_ram", Integer)
    messages_persistent = Column("messages_persistent", Integer)
    consumer_utilisation = Column("consumer_utilisation", String(20))
    messages_paged_out = Column("messages_paged_out", Integer)
    message_bytes_ram = Column("message_bytes_ram", Integer)
    messages_details_rate = Column("messages_details_rate", Integer)
    messages_unacknowledged_details_rate = Column(
        "messages_unacknowledged_details_rate", Integer)
    messages_ready_details_rate = Column("messages_ready_details_rate", Integer)
    avg_ingress_rate = Column("avg_ingress_rate", Integer)
    avg_ack_ingress_rate = Column("avg_ack_ingress_rate", Integer)
    avg_egress_rate = Column("avg_egress_rate", Integer)
    avg_ack_egress_rate = Column("avg_ack_egress_rate", Integer)
    stats_get_no_ack_details_rate = Column("stats_get_no_ack_details_rate",
                                           Integer)
    stats_deliver_no_ack = Column("stats_deliver_no_ack", Integer)
    stats_publish_details_rate = Column("stats_publish_details_rate", Integer)
    stats_ack = Column("stats_ack", Integer)
    stats_deliver = Column("stats_deliver", Integer)
    stats_deliver_get = Column("stats_deliver_get", Integer)
    stats_get_empty_details_rate = Column("stats_get_empty_details_rate",
                                          Integer)
    stats_redeliver = Column("stats_redeliver", Integer)
    stats_get_details_rate = Column("stats_get_details_rate", Integer)
    stats_deliver_get_details_rate = Column("stats_deliver_get_details_rate",
                                            Integer)
    stats_deliver_no_ack_details_rate = Column(
        "stats_deliver_no_ack_details_rate", Integer)
    stats_get_empty = Column("stats_get_empty", Integer)
    stats_get_no_ack = Column("stats_get_no_ack", Integer)
    stats_deliver_details_rate = Column("stats_deliver_details_rate", Integer)
    stats_get = Column("stats_get", Integer)
    stats_publish = Column("stats_publish", Integer)
    stats_ack_details_rate = Column("stats_ack_details_rate", Integer)
    stats_reductions_details_rate = Column("stats_reductions_details_rate",
                                           Integer)

    benchmark_session = Column("benchmark_session", String(40))
    created_time = Column("created_time", TIMESTAMP)
    idle_since = Column("idle_since", TIMESTAMP)


class BotDetectionStepResult(Base):
    __tablename__ = 'bot_detection_step_result'
    id = Column(Integer, primary_key=True)
    url = Column("url", String(700), index=True)
    proxy = Column("proxy", String(50))
    status_code = Column("status_code", Integer, default=None)
    browserless = Column('browserless', TINYINT)
    recaptcha = Column('recaptcha', TINYINT)
    h_captcha = Column('h_captcha', TINYINT)
    unknown_captcha = Column('unknown_captcha', TINYINT)
    detect_akamai = Column('detect_akamai', TINYINT)

    created_date = Column("created_date", DateTime, default=func.now())
