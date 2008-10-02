'''
Base class for storing movies and songs. Defines 3 tables:
    Entity      - holds all entities: movies, songs, persons, rating, year, etc.
    Relation    - holds all relations between entities: eg. person x is the "composer" of movie y
    Identity    - groups entities into identical groups. Any two entities having the same group are identical entities

Requires a database called `songs` to function. To recreate, run the following on MYSQL:
    DROP DATABASE IF EXISTS `songs`;
    CREATE DATABASE `songs` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
'''

from sqlobject import *
import datetime, re, htmlload, time, sys, trans

def connect():
    '''Connect to the MySQL database songs. Must be called before using this module'''
    connection = connectionForURI("mysql://root@localhost/songs")
    sqlhub.processConnection = connection

def create():
    '''Create all tables required for this module, if required. Safe to call once per run, but at all required.'''
    Entity.createTable(ifNotExists=True)
    Relation.createTable(ifNotExists=True)
    Identity.createTable(ifNotExists=True)

__langs__ = ('hindi', 'tamil', 'telugu', 'kannada', 'malayalam', 'carnatic', 'hindustani', 'punjabi', 'bengali', 'gujarati', 'marathi')

class Entity(SQLObject):
    db   = EnumCol      ( enumValues=('', 'www.musicindiaonline.com', 'www.raaga.com', 'www.oosai.com', 'ww.smashits.com', 'www.musicplug.in', 'music.cooltoad.com', 'www.dishant.com', 'www.youtube.com', 'www.dhingana.com', 'www.mp3hungama.com', 'bollyfm.net') )
    type = EnumCol      ( enumValues=('index', 'movie', 'song', 'year', 'person', 'rating', 'duration', 'tag') )
    lang = EnumCol      ( enumValues=('',) + __langs__, default='' )
    num  = UnicodeCol   ( notNone=True,  length=250 )
    name = UnicodeCol   ( notNone=True,  length=250 )
    tran = UnicodeCol   ( notNone=False, length=250 )
    url  = UnicodeCol   ( notNone=True,  length=250 )
    date = DateTimeCol  ( notNone=False )

    # TODO: Create indexes from here?
    # keyIndex = DatabaseIndex('db', 'type', 'lang', 'num')
    # entityIndex = DatabaseIndex('type', 'lang', 'name')

    def read(self):
        print "Getting", self.lang, self.db, self.type, self.name, self.url
        return htmlload.decode_entities(htmlload.url('http://' + self.db + '/' + self.url))

class Relation(SQLObject):
    src  = ForeignKey   ( 'Entity' )
    tgt  = ForeignKey   ( 'Entity' )
    rel  = EnumCol      ( enumValues=('movie', 'song', 'composer', 'singer', 'lyricist', 'actor', 'director', 'producer', 'year', 'rating', 'duration', 'tag', 'instrument', 'raaga', 'beat', 'religion', 'deity', 'language') )
    # rel  = StringCol    ( length=16 )

class Identity(SQLObject):
    src  = ForeignKey   ( 'Entity' )
    grp  = IntCol       ( notNone=True )

def __clean__(s):
    s = re.sub('\s+', ' ', s).strip()       # Condense spaces, and trim ends
    return s

def entity(db, type, lang, num, name='', url='', date=datetime.datetime.min):
    '''Return entity defined by key = (db|type|lang|num). Create one if none exists. If non-keys are empty (e.g. name / url), update them'''
    num = __clean__(num)
    name = __clean__(name)
    url = __clean__(url)
    e = Entity.selectBy(db=db, type=type, lang=lang, num=num).getOne(None)
    if e:
        if not e.name and name: e.set(name=name)
        if not e.url  and url:  e.set(url=url)
    else:
        if type in ('movie', 'song', 'person'): tr = trans.trans(name, lang)
        else: tr = ''
        e = Entity(db=db, type=type, lang=lang, num=num, name=name, tran=tr, url=url, date=date)
    return e

def relate(src, rel, tgt):
    '''Return the relation if it exists. If not, create it'''
    return (Relation.selectBy(src=src, rel=rel, tgt=tgt).getOne(None)
        or  Relation(src=src, rel=rel, tgt=tgt))

def identical(entities):
    '''Make a list of entities identical'''
    group = {}
    ungrouped_entities = []
    for entity in entities:
        id = Identity.selectBy(src=entity).getOne(None)
        if id: group[id.grp] = 1
        else: ungrouped_entities.append(entity)

    groups = group.keys()
    if len(groups) > 1:
        raise Exception()
    else:
        if len(groups) == 1: grp = groups[0]
        else: grp = int(time.time() * 1000 % sys.maxint)
        for e in ungrouped_entities: Identity(src=e, grp=grp)

def identicals(entity):
    '''Return all entities that are identical to the given entity'''
    identicals = Identity.selectBy(src=entity).getOne(None)
    if identicals: return (id.src for id in Identity.selectBy(grp=identicals.grp))
    else:   return (entity,)

def relations(entity):
    '''Return all relations of an entity and its identicals'''
    for rel in Relation.select(Relation.q.src==entity, orderBy=Relation.q.rel): yield (rel.rel, rel.tgt)
    for rel in Relation.select(Relation.q.tgt==entity, orderBy=Relation.q.rel): yield (rel.rel, rel.src)
    pass
