import re

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float

Base = declarative_base()

def int_or_none(s):
    if s == "":
        return None
    return int(s)

_converters = {
        Integer: int_or_none,
        String: (lambda x: x),
        Float: float
        }

_time_re = re.compile("([0-9][0-9]):([0-9][0-9]):([0-9][0-9])")

def parse_time(s):
    """
    Parse a string time in the format hh:mm:ss into a number of minutes
    We ignore seconds because they are always zero for the Ottawa data
    """
    assert len(s) == 8, "bad time string %r"%s
    match = _time_re.match(s)
    assert match
    hours_s, minutes_s = match.group(1, 2)
    hours = int(hours_s)
    minutes = int(minutes_s)
    return hours*60 + minutes

class Mixin(object):
    def __init__(self, **kargs):
        for k, v in kargs.items():
            if k in self.ignore_fields:
                continue
            columns = self.__table__.columns
            assert k in columns, "Missing column %r in table %r" % (
                    k, self.__tablename__)
            field_type = columns[k].type.__class__
            field_converter = _converters[field_type]
            try:
                setattr(self, k, field_converter(v))
            except Exception:
                raise RuntimeError("Problem converting field %r value %r" %
                        (k, v))

class ServiceDay(Mixin, Base):
    __tablename__ = 'days'

    ignore_fields = ()
    service_mapping = {}

    _id = Column(Integer, primary_key=True)
    # Note that a single day can indeed have multiple rows for multiple
    # services
    date = Column(String, index=True)
    service_id = Column(Integer)

class Stop(Mixin, Base):
    __tablename__ = 'stops'

    ignore_fields = ('stop_desc', 'stop_url', 'location_type', 'zone_id')
    mapping = {}

    _id = Column(Integer, primary_key=True)
    stop_id = Column(String, unique=True)
    stop_code = Column(String, index=True)
    stop_name = Column(String)
    stop_lat = Column(Float)
    stop_lon = Column(Float)

    def __init__(self, *, stop_id, **kargs):
        id = len(Stop.mapping)
        assert stop_id not in Stop.mapping
        Stop.mapping[stop_id] = id
        super().__init__(_id=id, stop_id=stop_id, **kargs)

class Route(Mixin, Base):
    __tablename__ = 'routes'

    ignore_fields = ('route_long_name', 'route_desc', 'route_type', 'route_url')

    route_id = Column(String, primary_key=True)
    route_short_name = Column(String, index=True)

class Trip(Mixin, Base):
    __tablename__ = 'trips'

    ignore_fields = ()
    mapping = {}

    trip_id = Column(Integer, primary_key=True)
    route_id = Column(String, ForeignKey('routes.route_id'), index=True)
    service_id = Column(Integer, ForeignKey('days.service_id'), index=True,
            nullable=False)
    trip_headsign = Column(String)
    direction_id = Column(Integer)
    block_id = Column(Integer)

    def __init__(self, *, trip_id, service_id, **kargs):
        new_id = len(Trip.mapping)
        Trip.mapping[trip_id] = new_id
        service_id = ServiceDay.service_mapping[service_id]
        super().__init__(trip_id=new_id, service_id=service_id, **kargs)

class StopTime(Mixin, Base):
    __tablename__ = 'stop_times'

    ignore_fields = ('departure_time')

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.trip_id'), index=True)
    arrival_time = Column(Integer) # in minutes from midnight
    stop_id = Column(Integer, ForeignKey('stops._id'), index=True)
    stop_sequence = Column(Integer)
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)

    def __init__(self, *, trip_id, stop_id, arrival_time, **kargs):
        trip_id = Trip.mapping[trip_id]
        stop_id = Stop.mapping[stop_id]
        arrival_time = parse_time(arrival_time)
        super().__init__(
                trip_id=trip_id, stop_id=stop_id,
                arrival_time=arrival_time, **kargs)

