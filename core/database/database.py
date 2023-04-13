import typing

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session

from .constants import CredentialsType as cred_type
from .entities import Base, Project, ProjectSession, Credential, BenchmarkStatistic


class AcceleratorDatabase:

    def __init__(self, database_url: str = None, session: Session = None):
        if session:
            self.engine = session.get_bind()
            self.session = session
        elif database_url:
            self.engine = create_engine(database_url, echo=False)
            self.session = self.create_session()
        else:
            raise ValueError('You must pass at least the one param!')
        Base.metadata.create_all(self.engine)

    def __del__(self):
        if self.session:
            self.session.close()

    def create_session(self) -> Session:
        return Session(bind=self.engine)

    def get_project_by_name(self, project_name: str) -> Project:
        item = self.session \
            .query(Project) \
            .filter(Project.project_name == project_name).first()
        return item

    def get_project_by_id(self, project_id: int) -> Project:
        item = self.session \
            .query(Project) \
            .filter(Project.id == project_id).first()
        return item

    def get_project_by_session_uniq_id(self, session_uniq_id: str) -> Project:
        session = self.session \
            .query(ProjectSession) \
            .filter(ProjectSession.session_id == session_uniq_id).first()
        project_by_session = self.session \
            .query(Project) \
            .filter(Project.id == session.project_id).first()
        return project_by_session

    def get_all_projects(self) -> typing.List[Project]:
        items = self.session.query(Project).all()
        return items

    def get_all_sessions(self) -> typing.List[ProjectSession]:
        items = self.session.query(ProjectSession).all()
        return items

    def get_sessions_by_project_id(self, project_id: int) -> typing.List[ProjectSession]:
        items = self.session \
            .query(ProjectSession) \
            .filter(ProjectSession.project_id == project_id).all()
        return items

    def get_sessions_by_project_name(self, project_name: str) -> typing.List[ProjectSession]:
        project_by_name = self.get_project_by_name(project_name)
        project_sessions = self.session \
            .query(ProjectSession) \
            .filter(ProjectSession.project_id == project_by_name.id).all()
        return project_sessions

    def get_active_sessions_by_project_name(self, project_name: str) -> typing.List[ProjectSession]:
        project_by_name = self.get_project_by_name(project_name)
        project_sessions = self.session \
            .query(ProjectSession) \
            .filter(and_(ProjectSession.project_id == project_by_name.id, ProjectSession.is_active is True)).all()
        return project_sessions

    def get_active_sessions(self) -> typing.List[ProjectSession]:
        project_sessions = self.session \
            .query(ProjectSession) \
            .filter(ProjectSession.is_active is True).all()
        return project_sessions

    def get_all_credential(self) -> typing.List[Credential]:
        items = self.session.query(Credential).all()
        return items

    def get_default_notifier_credential(self) -> Credential:
        items = self.session.query(Credential) \
            .filter(Credential.cred_type == cred_type.NOTIFIER_DEFAULT).first()
        return items

    def get_buffered_uploader_credential(self) -> Credential:
        items = self.session.query(Credential) \
            .filter(Credential.cred_type == cred_type.UPLOADER_BUFFERED).first()
        return items

    def get_all_notifier_credentials(self) -> typing.List[Credential]:
        items = self.session.query(Credential) \
            .filter(Credential.cred_type == cred_type.NOTIFIER).all()
        return items

    def get_all_uploader_credentials(self) -> typing.List[Credential]:
        items = self.session.query(Credential) \
            .filter(Credential.cred_type == cred_type.UPLOADER).all()
        return items

    def get_all_benchmark_stats_by_benchmark_session_id(self, session) \
            -> typing.List[BenchmarkStatistic]:

        items = self.session.query(BenchmarkStatistic) \
            .filter(BenchmarkStatistic.benchmark_session == session).all()
        return items

    def get_credentials_by_project_name_and_credentials_type_and_cred_type_content(
            self, project: str,
            cred_type: str,
            cred_content_type: str) -> Credential:

        cred_content_type = f'%"{cred_content_type}"%'

        item = self.session.query(Credential).filter(
            and_(Credential.cred_type == cred_type, Credential.content.like(cred_content_type))) \
            .filter(Credential.projects.any(Project.project_name == project)) \
            .first()

        return item

    def get_all_benchmark_stats_by_benchmark_session_id_and_queue_name(self, session, queue_name) \
            -> typing.List[BenchmarkStatistic]:

        items = self.session \
            .query(BenchmarkStatistic) \
            .filter(and_(BenchmarkStatistic.benchmark_session == session, BenchmarkStatistic.name == queue_name)).all()
        return items

    def save(self, obj) -> typing.Union:
        self.session.add(obj)
        self.session.commit()

    def save_all(self, objects) -> typing.Union:
        self.session.add_all(objects)
        self.session.commit()
