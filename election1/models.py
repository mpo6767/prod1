from sqlalchemy.orm import joinedload

from election1.extensions import db
from flask_login import UserMixin
from datetime import datetime
from election1.utils import unique_security_token
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
class BallotType(db.Model):
    """
    Represents the type of ballot used in the election.
    """
    id_ballot_type = db.Column(db.Integer, primary_key=True)
    ballot_type_name = db.Column(db.String(length=45), nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    offices = db.relationship('Office', backref='ballot_type', cascade="all, delete-orphan")

    @classmethod
    def check_if_exists(cls, ballot_type_name):
        """
        Check if a BallotType with the given name exists in the database.
        :param ballot_type_name: The name of the BallotType to check.
        :return: True if the BallotType exists, False otherwise.
        """
        return cls.query.filter_by(ballot_type_name=ballot_type_name).first() is not None

    @classmethod
    def get_all_ballot_types_sorted_by_name(cls):
        """
        Retrieve all BallotType records sorted by ballot_type_name.
        :return: A tuple of BallotType objects sorted by ballot_type_name.
        """
        return tuple((c.id_ballot_type, c.ballot_type_name) for c in cls.query.order_by(cls.id_ballot_type).all())

    # @classmethod
    # def get_ballot_type_name_by_id(cls, id_ballot_type):
    #     """
    #     Retrieve the ballot_type_name for a given BallotType ID.
    #     :param id_ballot_type: The ID of the BallotType to retrieve.
    #     :return: The ballot_type_name if found, otherwise None.
    #     """
    #     ballot_type = cls.query.filter_by(id_ballot_type=id_ballot_type).first()
    #     return ballot_type.ballot_type_name if ballot_type else None


class Classgrp(db.Model):
    """
    Represents a class or group in the election system.
    """
    id_classgrp = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=45), nullable=False, unique=True)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    candidates = db.relationship('Candidate', cascade="all, delete-orphan", backref='classgrp')


    @classmethod
    def classgrp_query(cls):
        return [(c.id_classgrp, c.name) for c in cls.query.order_by(cls.sortkey).all()]

class BallotMeasure(db.Model):
    """
    Represents a ballot measure in the election.
    """
    id_ballot_measure = db.Column(db.Integer, primary_key=True)
    ballot_measure_title = db.Column(db.String(length=45), nullable=False, unique=True)
    ballot_measure_description = db.Column(db.String(length=255), nullable=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    offices = db.relationship('Office', backref='ballot_measure', cascade="all, delete-orphan")


class Office(db.Model):
    """
    Represents an office for which candidates can run in the election.
    """
    id_office = db.Column(db.Integer, primary_key=True)
    office_title = db.Column(db.String(length=45), nullable=False, unique=True)
    office_vote_for = db.Column(db.Integer, default=1, nullable=False)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_ballot_type = db.Column(db.Integer, db.ForeignKey('ballot_type.id_ballot_type'), nullable=False)
    id_ballot_measure = db.Column(db.Integer, db.ForeignKey('ballot_measure.id_ballot_measure'), nullable=True)
    candidates = db.relationship('Candidate', cascade="all, delete-orphan", backref='office')

    @classmethod
    def office_query(cls):
        return [
            (o.id_office, o.office_title, b.ballot_type_name)
            for o, b in db.session.query(cls, BallotType)
            .join(BallotType, cls.id_ballot_type == BallotType.id_ballot_type)
            .order_by(cls.sortkey)
            .all()
        ]

    @classmethod
    def query_offices_for_classgroup_with_details_as_list(cls, classgroup_name):
        offices = db.session.query(
            cls.office_title,
            cls.sortkey,
            cls.office_vote_for
        ).join(Candidate).join(Classgrp).filter(
            Classgrp.name == classgroup_name
        ).distinct().order_by(cls.sortkey).all()

        return [[office.office_title, office.sortkey, office.office_vote_for] for office in offices]

    @classmethod
    def check_existing_office_title(cls, office_title):
        """
        Check if an office with the given title exists in the database.
        :param office_title: The title of the office to check.
        :return: True if the office exists, False otherwise.
        """
        return cls.query.filter_by(office_title=office_title).first() is not None


    @classmethod
    def get_ballot_type_name(cls, id_office):
        """
        Retrieve the ballot_type_name for a given office ID.
        :param id_office: The ID of the office.
        :return: The ballot_type_name if found, otherwise None.
        """
        office = db.session.query(cls).filter_by(id_office=id_office).first()
        return office.ballot_type.ballot_type_name if office and office.ballot_type else None

class Party(db.Model):
    """
    Represents a political party in the election system.
    """
    id_party = db.Column(db.Integer, primary_key=True)
    party_name = db.Column(db.String(length=45), nullable=False, unique=True)
    party_abbreviation = db.Column(db.String(length=1   ), nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    candidates = db.relationship('Candidate', backref='party', cascade="all, delete-orphan")

    @classmethod
    def get_all_parties_ordered_by_name(cls):
        """
        Retrieve all Party records ordered by party_name.
        :return: A tuple of tuples containing (id_party, party_name).
        """
        return tuple((party.id_party, party.party_name) for party in cls.query.order_by(cls.party_name).all())

class Candidate(db.Model):
    """
    Represents a candidate running for an office in a specific class or group.
    """
    id_candidate = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(length=45), nullable=False)
    lastname = db.Column(db.String(length=45), nullable=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_classgrp = db.Column(db.Integer, db.ForeignKey('classgrp.id_classgrp'), nullable=False)
    id_office = db.Column(db.Integer, db.ForeignKey('office.id_office'), nullable=False)
    id_party = db.Column(db.Integer, db.ForeignKey('party.id_party'), nullable=True)
    votes = db.relationship('Votes', backref='candidate')

    @classmethod
    def get_candidates_for_specific_office_by_classgrp(cls, choices_classgrp, choices_office):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).filter(Classgrp.id_classgrp == choices_classgrp, Office.id_office == choices_office)

    @classmethod
    def get_candidates_for_all_offices_by_classgrp(cls, choices_classgrp):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).filter(Classgrp.id_classgrp == choices_classgrp)


    @classmethod
    def candidate_search(cls, group):
        return db.session.query(
            cls,
            Classgrp,
            Office,
            Party.party_abbreviation.label('party_abbreviation')
        ).select_from(cls).join(Classgrp).join(Office).outerjoin(Party).order_by(
            Classgrp.sortkey, Office.sortkey
        ).where(Classgrp.id_classgrp == group)

    @classmethod
    def check_and_insert_writein_candidate(cls, choices_classgrp, choices_office):
        existing_candidate = cls.query.filter_by(
            firstname="Writein",
            lastname="Candidate",
            id_classgrp=choices_classgrp,
            id_office=choices_office
        ).first()

        if not existing_candidate:
            new_candidate = cls(
                firstname="Writein",
                lastname="Candidate",
                id_classgrp=choices_classgrp,
                id_office=choices_office
            )
            db.session.add(new_candidate)

    @classmethod
    def check_writein_candidate(cls, id_classgrp, id_office):
        return cls.query.filter_by(
            firstname='Writein',
            id_classgrp=id_classgrp,
            id_office=id_office
        ).first() is not None

    @classmethod
    def get_candidates_by_classgrp(cls, classgrp_id):
        return db.session.query(
            cls,
            Classgrp.name.label('classgrp_name'),
            Office.office_title.label('office_title')
        ).join(Classgrp).join(Office).filter(cls.id_classgrp == classgrp_id).order_by(Classgrp.sortkey, Office.sortkey).all()


    @classmethod
    def check_existing_candidate(cls, firstname, lastname, id_classgrp):
        return cls.query.filter_by(
            firstname=firstname,
            lastname=lastname,
            id_classgrp=id_classgrp
        ).first() is not None



    @classmethod
    def get_candidates_by_office(cls, office_id):
        from sqlalchemy.orm import joinedload

        candidates = cls.query.options(
            joinedload(cls.classgrp),  # Load related ClassGroup
            joinedload(cls.office)  # Load related Office
        ).filter_by(id_office=office_id).all()

        return [
            {
                "firstname": candidate.firstname,
                "lastname": candidate.lastname,
                "classgroup_name": candidate.classgrp.name if candidate.classgrp else "No Class Group",
                "office_name": candidate.office.office_title if candidate.office else "No Office"
            }
            for candidate in candidates
        ]
    @classmethod
    def get_summary_results(cls):
        """
        Retrieve summarized voting results grouped by class group and office.
        """
        return db.session.query(
            Classgrp.name.label('group_name'),  # record[0]
            Office.office_title.label('office_title'),  # record[1]
            Office.office_vote_for.label('vote_for'),  # record[2]
            Candidate.firstname.label('candidate_firstname'),  # record[3]
            Candidate.lastname.label('candidate_lastname'),  # record[4]
            Candidate.id_candidate.label('candidate_id'),  # record[5]
            func.count(Votes.id_candidate).label('vote_total')  # record[6]
        ).join(Votes, Votes.id_candidate == Candidate.id_candidate) \
            .join(Office, Candidate.id_office == Office.id_office) \
            .join(Classgrp, Candidate.id_classgrp == Classgrp.id_classgrp) \
            .group_by(
            Classgrp.name,
            Office.office_title,
            Office.office_vote_for,
            Candidate.firstname,
            Candidate.lastname,
            Candidate.id_candidate
        ) \
            .order_by(Classgrp.sortkey, Office.sortkey, func.count(Votes.id_candidate).desc()) \
            .all()

class User(db.Model, UserMixin):
    """
    Represents a user in the system, including admin users.
    """
    id_user = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(length=45), nullable=False)
    user_lastname = db.Column(db.String(length=45), nullable=False)
    user_so_name = db.Column(db.String(length=30), nullable=False, unique=True)
    user_pass = db.Column(db.String(length=256))
    user_email = db.Column(db.String(length=45), unique=True)
    user_status = db.Column(db.Integer, default=False, nullable=False)
    user_pw_change = db.Column(db.String(length=1))
    user_security = db.Column(db.String(138), default=unique_security_token)
    user_created = db.Column(db.DateTime, default=datetime.now)
    user_sec_send = db.Column(db.DateTime, default=datetime.now)
    user_creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_admin_role = db.Column(db.Integer, db.ForeignKey('admin_roles.id_admin_role'))

    def get_id(self):
        """
        Return the unique identifier for the user.
        """
        return self.id_user

    @classmethod
    def get_all_admins(cls):
        return db.session.query(cls, Admin_roles).select_from(cls).join(Admin_roles).order_by()

    @classmethod
    def get_user_by_so_name(cls, so_name):
        return cls.query.filter_by(user_so_name=so_name).first()


class Admin_roles(db.Model):
    """
    Represents the roles that admin users can have.
    """
    id_admin_role = db.Column(db.Integer, primary_key=True)
    admin_role_name = db.Column(db.String(length=45), nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user = db.relationship('User', backref='admin_roles')


class Dates(db.Model):
    """
    Represents the start and end dates for an election.
    """
    iddates = db.Column(db.Integer, primary_key=True)
    start_date_time = db.Column(db.Integer, nullable=False)
    end_date_time = db.Column(db.Integer, nullable=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @classmethod
    def after_start_date(cls):
        date = cls.query.first()
        if date:
            start_date_time = datetime.fromtimestamp(date.start_date_time)
            current_date_time = datetime.now()
            return current_date_time > start_date_time
        return False

    @classmethod
    def check_dates(cls):
        date = cls.query.first()
        return date is not None


class Votes(db.Model):
    """
    Represents a vote cast by a user.
    If there is a write-in candidate, the write-in candidate will be store
    in the votes_writein_name field.
    """
    id_votes = db.Column(db.Integer, primary_key=True)
    votes_token = db.Column(db.String(138), nullable=False)
    votes_writein_name = db.Column(db.String(45), nullable=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_candidate = db.Column(db.Integer, db.ForeignKey('candidate.id_candidate'))


class WriteinCandidate(db.Model):
    """
    Represents a write-in candidate.
    The write-in candidate nust be registered by an admin user.
    """
    id_writein_candidate = db.Column(db.Integer, primary_key=True)
    writein_candidate_name = db.Column(db.String(45), nullable=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_office = db.Column(db.Integer, db.ForeignKey('office.id_office'))
    id_classgrp = db.Column(db.Integer, db.ForeignKey('classgrp.id_classgrp'))

    @classmethod
    def get_writein_candidates_sorted(cls):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey).all()

    @classmethod
    def check_existing_writein_candidate(cls, writein_candidate_name, id_classgrp, id_office):
        return cls.query.filter_by(
            writein_candidate_name=writein_candidate_name,
            id_classgrp=id_classgrp,
            id_office=id_office
        ).first() is not None


class Tokenlist(db.Model):
    """
    Represents a list of tokens used for voting.
    """
    id_tokenlist = db.Column(db.Integer, primary_key=True)
    grp_list = db.Column(db.String(45), nullable=False)
    token = db.Column(db.String(138), nullable=False,unique=True)
    vote_submitted_date_time = db.Column(db.DateTime, nullable=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)



    def to_dict(self):
        """
        Convert the Tokenlist object into a dictionary format.
        """
        return {
            'id_tokenlist': self.id_tokenlist,
            'grp_list': self.grp_list,
            'token': self.token,
            'vote_submitted_date_time': self.vote_submitted_date_time.isoformat() if self.vote_submitted_date_time else None
        }

    @classmethod
    def get_tokenlist_record(cls, token):
        """
        Retrieve a Tokenlist record if the given token exists in the Tokenlist.
        :param token: The token to search for in the Tokenlist.
        :return: The Tokenlist record as a dictionary .
         """
        token_record = cls.query.filter_by(token=token).first()

        if token_record is None:
            # Token does not exist
            return {'error': 'Invalid token'}
        if token_record.vote_submitted_date_time is not None:
            # Token exists but vote has been submitted
            return {'error': 'Token has already been used'}
        return token_record.to_dict()

class Tokenlistselectors(db.Model):

    id_tokenListSelector = db.Column(db.Integer, primary_key=True)
    primary_grp = db.Column(db.String(45), nullable=False)
    secondary_grp = db.Column(db.String(45))
    tertiary_grp = db.Column(db.String(45))
    quarternary_grp = db.Column(db.String(45))
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @classmethod
    def get_all_tokenlistselectors(cls):
        return cls.query.all()

    def to_dict(self):
        return {
            'id_tokenListSelector': self.id_tokenListSelector,
            'primary_grp': self.primary_grp,
            'secondary_grp': self.secondary_grp,
            'tertiary_grp': self.tertiary_grp,
            'quarternary_grp': self.quarternary_grp,
            'creation_datetime': self.creation_datetime.isoformat()
        }
    @classmethod
    def get_all_tokenlistselectors_as_dict(cls):
        return [selector.to_dict() for selector in cls.query.all()]

    @classmethod
    def get_tokenlistselector_by_id_as_dict(cls, xid):
        """
        Retrieve a single Tokenlistselector by its ID and return it as a dictionary.
        :param xid: The ID of the Tokenlistselector to retrieve.
        :return: A dictionary representation of the Tokenlistselector if found, otherwise None.
        """
        tokenlistselector = cls.query.get(xid)
        if tokenlistselector:
            return {
                'id_tokenListSelector': tokenlistselector.id_tokenListSelector,
                'primary_grp': tokenlistselector.primary_grp,
                'secondary_grp': tokenlistselector.secondary_grp,
                'tertiary_grp': tokenlistselector.tertiary_grp,
                'quarternary_grp': tokenlistselector.quarternary_grp
            }
        return None

