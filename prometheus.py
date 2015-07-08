#Prometheus creates the database that will house all data. It is currently designed with a MySQL database engine.
import os
import sys
from sqlalchemy import Column, Integer, String, Float, create_engine, __version__
from sqlalchemy.ext.declarative import declarative_base

#Check which version of SQLAlchemy is currently being used.
print "Current SQLAlchemy Version: " + __version__

Base = declarative_base()

#Creating the table using SQLAlchemy's Table and Column objects.
class Olympus(Base):
	__tablename__ = 'olympus'
	id					= Column(Integer,    primary_key=True)
	project				= Column(String(30), nullable=False)
	uid					= Column(String(50), nullable=False)
	provider			= Column(String(30), nullable=False)
	region				= Column(String(30), nullable=False)
	startdate			= Column(String(30), nullable=False)
	processor			= Column(String(30), nullable=False)
	vm 					= Column(String(30), nullable=False)
	vmcount				= Column(Integer,    nullable=False)
	vcpu 				= Column(Integer,    nullable=False)
	ram					= Column(Float(30),  nullable=False)
	local 				= Column(Integer,    nullable=False)
	block				= Column(Integer,    nullable=False)
	disk_rand           = Column(String(10), nullable=True)
	disk_seq            = Column(String(10), nullable=True)
	disk_blocksize      = Column(String(10), nullable=True)
	disk_filesize       = Column(String(10), nullable=True)
	disk_numjobs        = Column(String(10), nullable=True)
	disk_direct         = Column(String(10), nullable=True)

class Hermes_System(Base):
	__tablename__ = 'system'
	id					= Column(Integer,    primary_key=True)
	uid					= Column(String(50), nullable=True)
	iteration			= Column(Integer,    nullable=True)
	runtime             = Column(Float(30),  nullable=True)
	intmulti			= Column(Integer,    nullable=True)
	floatmulti			= Column(Integer,    nullable=True)
	memmulti			= Column(Integer,    nullable=True)
	totalmulti			= Column(Integer,    nullable=True)
	aes 				= Column(Float(30),  nullable=True)
	twofish				= Column(Float(30),  nullable=True)
	sha1				= Column(Float(30),  nullable=True)
	sha2				= Column(Float(30),  nullable=True)
	bzipcompression 	= Column(Float(30),  nullable=True)
	bzipdecompression 	= Column(Float(30),  nullable=True)
	jpegcompression 	= Column(Float(30),  nullable=True)
	jpegdecompression 	= Column(Float(30),  nullable=True)
	pngcompression 		= Column(Float(30),  nullable=True)
	pngdecompression 	= Column(Float(30),  nullable=True)
	sobel 				= Column(Float(30),  nullable=True)
	lua 				= Column(Float(30),  nullable=True)
	dijkstra			= Column(Float(30),  nullable=True)
	blackscholes		= Column(Float(30),  nullable=True)
	mandelbrot			= Column(Float(30),  nullable=True)
	sharpenimage		= Column(Float(30),  nullable=True)
	blurimage			= Column(Float(30),  nullable=True)
	sgemm				= Column(Float(30),  nullable=True)
	dgemm				= Column(Float(30),  nullable=True)
	sfft				= Column(Float(30),  nullable=True)
	dfft				= Column(Float(30),  nullable=True)
	nbody				= Column(Float(30),  nullable=True)
	raytrace			= Column(Float(30),  nullable=True)
	copy				= Column(Float(30),  nullable=True)
	scale				= Column(Float(30),  nullable=True)
	add					= Column(Float(30),  nullable=True)
	triad				= Column(Float(30),  nullable=True)

class HermesRand(Base):
	__tablename__ = 'random_disk'
	id                  = Column(Integer,    primary_key=True)
	uid                 = Column(String(50), nullable=True)
	iteration           = Column(Integer,    nullable=True)
	read_runtime        = Column(Float(30),  nullable=True)
	write_runtime       = Column(Float(30),  nullable=True)
	read_iops           = Column(Float(30),  nullable=True)
	read_io             = Column(Float(30),  nullable=True)
	read_bw             = Column(Float(30),  nullable=True)
	read_ticks          = Column(Float(30),  nullable=True)
	write_iops          = Column(Float(30),  nullable=True)
	write_io            = Column(Float(30),  nullable=True)
	write_bw            = Column(Float(30),  nullable=True)
	write_ticks         = Column(Float(30),  nullable=True)

class HermesSeq(Base):
	__tablename__ = 'sequential_disk'
	id                  = Column(Integer,    primary_key=True)
	uid                 = Column(String(50), nullable=True)
	iteration           = Column(Integer,    nullable=True)
	read_runtime        = Column(Float(30),  nullable=True)
	write_runtime       = Column(Float(30),  nullable=True)
	read_iops           = Column(Float(30),  nullable=True)
	read_io             = Column(Float(30),  nullable=True)
	read_bw             = Column(Float(30),  nullable=True)
	read_ticks          = Column(Float(30),  nullable=True)
	write_iops          = Column(Float(30),  nullable=True)
	write_io            = Column(Float(30),  nullable=True)
	write_bw            = Column(Float(30),  nullable=True)
	write_ticks         = Column(Float(30),  nullable=True)

class HermesRandasync(Base):
	__tablename__ = 'random_disk_async'
	extend_existing=True
	id                  = Column(Integer,    primary_key=True)
	uid                 = Column(String(50), nullable=True)
	iteration           = Column(Integer,    nullable=True)
	read_runtime        = Column(Float(30),  nullable=True)
	write_runtime       = Column(Float(30),  nullable=True)
	read_iops           = Column(Float(30),  nullable=True)
	read_io             = Column(Float(30),  nullable=True)
	read_bw             = Column(Float(30),  nullable=True)
	read_ticks          = Column(Float(30),  nullable=True)
	write_iops          = Column(Float(30),  nullable=True)
	write_io            = Column(Float(30),  nullable=True)
	write_bw            = Column(Float(30),  nullable=True)
	write_ticks         = Column(Float(30),  nullable=True)

class HermesSeqasync(Base):
	__tablename__ = 'sequential_disk_async'
	extend_existing=True
	id                  = Column(Integer,    primary_key=True)
	uid                 = Column(String(50), nullable=True)
	iteration           = Column(Integer,    nullable=True)
	read_runtime        = Column(Float(30),  nullable=True)
	write_runtime       = Column(Float(30),  nullable=True)
	read_iops           = Column(Float(30),  nullable=True)
	read_io             = Column(Float(30),  nullable=True)
	read_bw             = Column(Float(30),  nullable=True)
	read_ticks          = Column(Float(30),  nullable=True)
	write_iops          = Column(Float(30),  nullable=True)
	write_io            = Column(Float(30),  nullable=True)
	write_bw            = Column(Float(30),  nullable=True)
	write_ticks         = Column(Float(30),  nullable=True)

class HermesNet(Base):
	__tablename__ = 'internal_network'
	id                  = Column(Integer,    primary_key=True)
	uid                 = Column(String(50), nullable=True)
	iteration           = Column(Integer,    nullable=True)
	transfer_mb			= Column(Float(30),  nullable=True)
	bandwidth_mb		= Column(Float(30),  nullable=True) 

class HermesPTS(Base):
	__tablename__ = 'pts'
	id                  = Column(Integer,    primary_key=True)
	uid                 = Column(String(50), nullable=True)
	iteration           = Column(Integer,    nullable=True)
	compress7zip		= Column(Float(30),	 nullable=True)
	phpbench			= Column(Float(30),    nullable=True)
	mp3encode			= Column(Float(30),    nullable=True)
	x264				= Column(Float(30),    nullable=True)

#Create an object, db, to act as the connect to the database.
#The SQLEngine object is used to open the connection, which is what is being used in the db variable. 
#Format for create_engine is "engine://user:password@host:port/database"
Ignition = create_engine("mysql://2vcpu:800BoylstonClouds@104.131.127.149:3306/omnipotentzeus2")

#Holds all the database metadata.
Base.metadata.create_all(Ignition)
