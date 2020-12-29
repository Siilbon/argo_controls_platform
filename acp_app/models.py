from . import db


class Teammate(db.Model):
    __tablename__ = 'teammates'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)
    name = db.Column(db.String(64), unique=True)
    role = db.Column(db.String(64))
    units = db.relationship('Unit', backref='teammate', lazy='dynamic')
    email = db.Column(db.String(64))
    linkedin = db.Column(db.String(64))

    def __repr__(self):
        return f'<Teammate {self.name}>'


class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    teammate_id = db.Column(db.Integer, db.ForeignKey('teammates.id'))

    def __repr__(self):
        return f'<Unit {self.name}>'


class IntellutionTag(db.Model):
    __tablename__ = 'intellution_tags'
    index = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    tag = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    ft_topic = db.Column(db.String(64))
    ioad = db.Column(db.String(64))
    source = db.Column(db.String(64))
    opc_topic = db.Column(db.String(64))
    ienab = db.Column(db.String(64))
    opendesc = db.Column(db.String(64))
    closedesc = db.Column(db.String(64))
    elo = db.Column(db.String(64))
    ehi = db.Column(db.String(64))
    egudesc = db.Column(db.String(64))
    pri = db.Column(db.String(64))
    sa1 = db.Column(db.String(64))
    sa2 = db.Column(db.String(64))
    sa3 = db.Column(db.String(64))
    all_areas = db.Column(db.String(64))
    almext1 = db.Column(db.String(64))
    almext2 = db.Column(db.String(64))
    prefix = db.Column(db.String(64))
    loop = db.Column(db.String(64))
    suffix = db.Column(db.String(64))
    alias_root = db.Column(db.String(64))
    alias_field = db.Column(db.String(64))
    alias_rest = db.Column(db.String(64))

    def __repr__(self):
        return f'<Intellution Tag {self.tag}>'