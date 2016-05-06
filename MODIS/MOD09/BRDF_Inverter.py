#!/usr/bin/env python

import glob
import os
import sys
import time

try:
	import statsmodels.api as sm
except ImportError:
	print 'StatsModel lib is not installed'
	exit(-1)

try:
	import osgeo.gdal as gdal
	from osgeo.gdalconst import *
	gdal.UseExceptions()
except ImportError:
	print 'GDAL is not installed.'
	exit(-1)

import datetime as DT
from matplotlib.dates import date2num

import numpy
import math

from scipy.linalg import lstsq, inv
from scipy.optimize import nnls

def GetStrDoY(DoY):

	if len(str(int(DoY))) == 1:
		strDoY = '00' + str(int(DoY))
	elif len(str(int(DoY))) == 2:
		strDoY = '0' + str(int(DoY))
	else:
		strDoY = str(int(DoY))

	return strDoY

def NormalDistribution(mu,sigma):
	def f(x):
		z = 1.0*(x-mu)/sigma
		e = math.e**(-0.5*z**2)
		C = math.sqrt(2*math.pi)*sigma
		return 1.0*e/C
	return f

def GetOutlierIndices(NIR_profile, JulianDoY):
	#ipshell = embed()
	indices = numpy.where(NIR_profile > 0.0)
	if indices[0].shape[0] < 7:
		outlier_indices = numpy.array([])
		return outlier_indices

	model = sm.OLS(NIR_profile[indices[0]], JulianDoY[indices[0]])
	results = model.fit()
	# Outlier detection using the Benjamini/Yekutieli false discovery rate (FDR) test
	#test = results.outlier_test(method='fdr_by')
	# Outlier detection using the holm-sidak test
	test = results.outlier_test(method='holm-sidak')
	normalized_p = test[:,2]
	# if the normalized p_value is smaller than 0.25 then the sample is flagged as outlier
	outlier_indices = numpy.where(normalized_p < 0.25)

	return indices[0][outlier_indices[0]]

def GetReflectances(ReflectancesFile, KernelsFile, Weigth, InitRow, InitCol, rows, cols, ProcessSnow):

	ReflScaleFactor = 10000.
	NumberOfBands = 7
	NumberOfParameters = 3

	# BBDR matrix size -> rows x columns x NumberOfBands x 1
	Reflectance = numpy.zeros((rows, cols, NumberOfBands, 1), numpy.float32)
	ReflectanceSD = numpy.zeros((rows, cols, NumberOfBands), numpy.float32)
	NumberOfSamples = numpy.zeros((rows, cols), numpy.float32)

	# Open dataset
	dataset = gdal.Open(ReflectancesFile, GA_ReadOnly)

	SnowMask = dataset.GetRasterBand( ( NumberOfBands * 2 ) + 1 ).ReadAsArray(InitCol,InitRow, cols ,rows)
	# Mask based on ProcessSnow
	if ProcessSnow == 1:
		SnowMask = numpy.where( SnowMask == 1, 1, 0)
	else:
		SnowMask = numpy.where( SnowMask == 1, 0, 1)

	for i in range(NumberOfBands):

		BandData = dataset.GetRasterBand(i+1).ReadAsArray(InitCol,InitRow, cols ,rows)
		Reflectance[:,:,i,0] = BandData / ReflScaleFactor * SnowMask

		BandData = dataset.GetRasterBand(i+NumberOfBands+1).ReadAsArray(InitCol,InitRow, cols ,rows)
		ReflectanceSD[:,:,i] = BandData / ReflScaleFactor * SnowMask

	SnowMask = dataset.GetRasterBand( ( NumberOfBands * 2 ) + 1 ).ReadAsArray(InitCol,InitRow, cols ,rows)

	dataset = None

	#-------------------------------------
	# Build C -- coveriance matrix for obs
	#-------------------------------------
	# C in a symetric matrix form of NumberOfBands * NumberOfBands
	C = numpy.zeros((rows, cols, NumberOfBands, NumberOfBands), numpy.float32)
	Cinv = numpy.zeros((rows, cols, NumberOfBands, NumberOfBands), numpy.float32)

	for i in range(NumberOfBands):
		C[:,:,i,i] = ReflectanceSD[:,:,i] * ReflectanceSD[:,:,i]

	# Create matrices: M, V and E
	# M = Kernels^T C^-1 Kernels
	# V = Kernels^T C^-1 Reflectance
	# E = Reflectance^T C^-1 Reflectance
	M = numpy.zeros((rows, cols, NumberOfBands*NumberOfParameters, NumberOfBands*NumberOfParameters), numpy.float32)
	V = numpy.zeros((rows, cols, NumberOfBands*NumberOfParameters), numpy.float32)
	E = numpy.zeros((rows, cols), numpy.float32)

	# Get Kernels
	Kernels = GetKernels(KernelsFile, InitRow, InitCol, rows, cols) 

	for j in range(0,cols):
		for i in range(0,rows):
			# Only process pixels where there are data in all three wavebands and NIR LT 0.72
			if numpy.where( (Reflectance[i,j,:]>0.0) & (Reflectance[i,j,:]<=1.0) )[0].shape[0] == NumberOfBands and \
               numpy.where( (ReflectanceSD[i,j,:]>=0.0) & (ReflectanceSD[i,j,:]<=1.0) )[0].shape[0] == NumberOfBands:

				Cinv[i,j,:,:] = numpy.matrix(C[i,j,:,:]).I
				M[i,j,:,:] = numpy.matrix(Kernels[i,j,:,:]).T * numpy.matrix(Cinv[i,j,:,:]) * numpy.matrix(Kernels[i,j,:,:])
				# Multiply only using lead diagonal of Cinv, additionally transpose the result to store V as a 1 x 9 vector
				V[i,j,:] = (numpy.matrix(Kernels[i,j,:,:]).T * numpy.diagflat(numpy.diagonal(Cinv[i,j,:,:])) * Reflectance[i,j,:,:]).T
				E[i,j] = numpy.matrix(Reflectance[i,j,:,:]).T * numpy.matrix(Cinv[i,j,:,:]) * Reflectance[i,j,:,:]
				NumberOfSamples[i,j] = Weigth

	return ReturnGetReflectances(Reflectance, M, V, E, NumberOfSamples, SnowMask)


class ReturnGetReflectances(object):
    def __init__(self, Reflectance, M, V, E, NumberOfSamples, SnowMask):
		self.Reflectance = Reflectance
		self.M = M
		self.V = V
		self.E = E
		self.NumberOfSamples = NumberOfSamples
		self.SnowMask = SnowMask


def GetKernels(KernelsFile, InitRow, InitCol, rows, cols):

	NumberOfBands = 7
	NumberOfKernels = 3

	Kernels = numpy.zeros((rows, cols, NumberOfBands, NumberOfKernels * NumberOfBands,), numpy.float32)
    # Isotropic kernels = 1
	for i in range(NumberOfBands):
		 Kernels[:,:,i,i*3] = 1.

	for i in range(1,NumberOfKernels):
		dataset = gdal.Open(KernelsFile, GA_ReadOnly)
		BandData = dataset.GetRasterBand(i).ReadAsArray(InitCol, InitRow, cols ,rows)
		for k in range(NumberOfBands):
			Kernels[:,:,k,(k*3)+i] = BandData

	dataset = BandData = None

	return Kernels


def GetPrior(PriorDataDir, strDoY, InitRow, InitCol, rows, cols, PriorScaleFactor = 10.0, Snow = 0):

	if int(strDoY) == 1:
		strDoY = "361"
	else:
		strDoY = GetStrDoY(int(strDoY) - 8)

	if Snow == 0:
		PriorFile = PriorDataDir + '/MCD43A2.Prior.' + strDoY + '.img'
	else:
		PriorFile = PriorDataDir + '/MCD43A2.SnowPrior.' + strDoY + '.img'

	print "Opening prior", PriorFile, "with scaling factor", PriorScaleFactor
	#rows, cols, NumberOfBands = GetDimensions(PriorFile)

	NumberOfBands = 7
	NumberOfParameters = 3

	Prior = numpy.zeros((rows,cols,NumberOfBands * NumberOfParameters), numpy.float32)
	PriorVariance = numpy.zeros((rows,cols,NumberOfBands * NumberOfParameters), numpy.float32)
	Mask = numpy.zeros((rows,cols), numpy.int8)

	C = numpy.zeros((rows, cols, NumberOfBands * NumberOfParameters, NumberOfBands * NumberOfParameters), numpy.float32)
	Cinv = numpy.zeros((rows, cols, NumberOfBands * NumberOfParameters, NumberOfBands * NumberOfParameters), numpy.float32)
	CinvF = numpy.zeros((rows, cols, NumberOfBands * NumberOfParameters), numpy.float32) # Matrix to store C^-1 * Fpr

	dataset = gdal.Open(PriorFile, GA_ReadOnly)
	for i in range(NumberOfBands * NumberOfParameters):
		BandData = dataset.GetRasterBand(i+1).ReadAsArray(InitCol,InitRow, cols ,rows)
		Prior[:,:,i] = BandData

		BandData = dataset.GetRasterBand(i + (NumberOfBands * NumberOfParameters) + 1).ReadAsArray(InitCol,InitRow, cols ,rows)
		# Could be the case that the covariance is 0 or very small but there are samples, make variance = 1
		PriorVariance[:,:,i] = numpy.where(BandData[:,:] <= 1.0e-8, 1.0, BandData[:,:])
		C[:,:,i,i] = PriorVariance[:,:,i] * PriorScaleFactor
		C[:,:,i,i] = numpy.where(C[:,:,i,i] > 1.0, 1.0, C[:,:,i,i])

	BandData = dataset = None

	# Calculate C inverse
	for j in range(0,cols):
		for i in range(0,rows):
			# Check that al least the isotropic parameters have values
			if numpy.where( (Prior[i,j,[0,3,6]]>0.0) & (Prior[i,j,[0,3,6]]<=1.0) )[0].shape[0] == 3:

				try:
					Cinv[i,j,:,:] = numpy.matrix(C[i,j,:,:]).I
				except numpy.linalg.LinAlgError:
					indices = numpy.where(PriorVariance[i,j,:] == 0.0)[0]
					PriorVariance[i,j,indices] = 1.0
					C[i,j,indices,indices] = 1.0
					Cinv[i,j,:,:] = numpy.matrix(C[i,j,:,:]).I

				for k in range(NumberOfBands * NumberOfParameters):
					CinvF[i,j,k] = Cinv[i,j,k,k] * Prior[i,j,k]

				Mask[i,j] = 1

	return ReturnPriorData(Cinv, CinvF, Prior, PriorVariance, Mask)


class ReturnPriorData(object):
	def __init__(self, M, V, Parameters, ParametersVariance, Mask):
		self.M = M
		self.V = V
		self.Parameters = Parameters
		self.ParametersVariance = ParametersVariance
		self.Mask = Mask

def IsLeapYear(Year):
	if Year % 4 == 0:
		if Year % 100 == 0:
			if Year % 400 == 0:
				return True
			else:
				return False
		else:
			return True
	else:
		return False

def GetFileList(strInitDoY, DataDir, Year):
	# Standard deviation and mean of the normal distribution to create the weighting factors    
	SD = 7
	mu = 16
	f = NormalDistribution(mu, SD)

	TimeWindow = 32
	FileList = []
	InitDoY = int(strInitDoY)

	# The DoY will be at the center of the 32-day time period
	for Day in range(InitDoY-(TimeWindow/2), InitDoY+(TimeWindow/2)):
		# Some Doy could be lower than 1
		# Assign the right DoY taking into account if Year is a leap-year
		if Day < 1 and IsLeapYear(Year):
			strYear = str(Year - 1)
			strDay = GetStrDoY(366 + Day)
		elif Day < 1 and not(IsLeapYear(Year)):
			strYear = str(Year - 1)
			strDay = GetStrDoY(365 + Day)
		# Some DoY could be greater than 365/366
		# Assign the right DoY taking into account if Year is a leap-year
		elif Day == 366 and IsLeapYear(Year):
			strYear = str(Year)
			strDay = GetStrDoY(Day)
		elif Day >= 366 and not(IsLeapYear(Year)):
			strYear = str(Year + 1)
			strDay = GetStrDoY(Day - 365)
		elif Day >= 367:
			if IsLeapYear(Year):
				strDay = GetStrDoY(Day - 366)
			else:
				strDay = GetStrDoY(Day - 365)
			strYear = str(Year + 1)
		else:
			strDay = GetStrDoY(Day)
			strYear = str(Year)

		#ipshell = embed()

		Files = glob.glob(DataDir + '/M?D09GA/VRTs/M?D09GA.' + strYear + strDay + '.h??v??.tif')
		for DailyFile in Files:
			FileList.append(DailyFile)

	#FileList.sort()

	Year = numpy.zeros((len(FileList)), numpy.int16)
	DoY = numpy.zeros((len(FileList)), numpy.int16)
	JulianDoY = numpy.zeros((len(FileList)), numpy.int16)
	Weigth = numpy.zeros((len(FileList)), numpy.float32)

	i = 0
	for j, File in enumerate( FileList ):
		# Get Year and DoY from filename
		YearOfObservation = os.path.basename(File).split('.')[1][0:4]
		DoYOfObservation = os.path.basename(File).split('.')[1][4:7]

		Year[j] = YearOfObservation
		DoY[j] = DoYOfObservation
		JulianDoY[j] = date2num(DT.datetime.strptime(YearOfObservation + DoYOfObservation, "%Y%j"))

		# Observations from the same DoY must have the same weight
		#ipshell = embed()
		if j == 0:
			DoYWeighting = j
			Weigth[j] = f(DoYWeighting)*((TimeWindow/2)-1)
		else:
			if DoY[j] ==  DoY[j-1]:
				DoYWeighting = i
				Weigth[j] = f(DoYWeighting)*((TimeWindow/2)-1)
			else:
				i += 1
				DoYWeighting = i 
				Weigth[j] = f(DoYWeighting)*((TimeWindow/2)-1)

	# Normalized Weigth
	Weigth = Weigth / Weigth.max()

	return FileList, Year, DoY, JulianDoY, Weigth


def GetDimensions(File):
	dataset = gdal.Open(File, GA_ReadOnly)
	# Usually the AVH09C1 layerstack should contain 10 bands
	rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
	dataset = None

	return rows, cols, NumberOfBands

def BRDF_Inverter(NIR_Reflectance, M, V, E,
                  Prior, PriorGapFiller,
                  NumberOfBands, NumberOfParameters, NumberOfSamples):

	rows, cols = E.shape
	Parameters = numpy.zeros((rows, cols, NumberOfBands, NumberOfParameters), numpy.float32)
	ParametersVariance = numpy.zeros((rows, cols, NumberOfBands, NumberOfParameters), numpy.float32)
	GoodnessOfFit = numpy.zeros((rows, cols), numpy.float32)

	for j in range(0,cols):
		if j % 100 == 0:
			print "Processing columns", j
		for i in range(0,rows):
			#if (Prior.Mask[i,j] == 1 and NumberOfSamples[i,j] > 0.0) or (NumberOfSamples[i,j] > 0.0):
			# The QA mask is not working  properly in some areas, therefore if not a single observation
			# was acquired on the 11-year time period for the climatology then, the LTDR observations can
			# be trusted completaly
			if ( Prior.Mask[i,j] == 1 and NumberOfSamples[i,j] >= 7.0 ):

				M_inversion = M[i,j,:,:] + Prior.M[i,j,:,:]
				V_inversion = V[i,j,:] + Prior.V[i,j,:]

				# (P, rho_residuals, rank, svals) = lstsq(M_inversion, V_inversion)
                # Non-negative least squares
				P = nnls(M_inversion, V_inversion)

				# If the prior has some parameters eq 0 is safer to do P for those indices 0
				indices = numpy.where(Prior.Parameters[i,j,:] == 0)
				#P[indices] = 0.0
				P[0][indices] = 0.0

				GoodnessOfFit[i,j] = (P[0] * numpy.matrix(M_inversion) * numpy.matrix(P[0]).T) + \
                                     (P[0] * numpy.matrix(V_inversion).T) - (2*E[i,j])
				Parameters[i,j,:,:] = P[0].reshape(NumberOfBands,NumberOfParameters)

				#GoodnessOfFit[i,j] = (P * numpy.matrix(M_inversion) * numpy.matrix(P).T) + \
                #                     (P * numpy.matrix(V_inversion).T) - (2*E[i,j])
				#Parameters[i,j,:,:] = P.reshape(NumberOfBands,NumberOfParameters)
				
				# Compute NIR BHR to compare with the original NIR samples statistics (min & max)
				f0, f1, f2 = Parameters[i,j,1,0], Parameters[i,j,1,1], Parameters[i,j,1,2]
				NIR_BHR = f0 + (f1 * 0.189184) + (f2 * -1.377622)
				
				# If the NIR_BHR is out of the input data range, use the prior as gap filler
				NominalUncert = 0.05
				if ( (NIR_BHR * (1 - NominalUncert)) > NIR_Reflectance[i,j,0] or 
                     (NIR_BHR * (1 + NominalUncert)) < NIR_Reflectance[i,j,1] ):
					GoodnessOfFit[i,j] = 0.0
					Parameters[i,j,:,:] = PriorGapFiller.Parameters[i,j,:].reshape(NumberOfBands,NumberOfParameters)
					ParametersVariance[i,j,:,:] = PriorGapFiller.ParametersVariance[i,j,:].reshape(NumberOfBands,NumberOfParameters)
				else:
					try:
						ParametersVariance[i,j,:,:] = numpy.diagonal(numpy.matrix(M_inversion).I).reshape(NumberOfBands,NumberOfParameters)
					except numpy.linalg.LinAlgError:
						# Set all off-diagonal elements of M_inversion to 0
						M_inversion_tmp = numpy.zeros((M_inversion.shape), numpy.float32)
						for k in range( NumberOfBands * NumberOfParameters ):
							M_inversion_tmp[k,k] = M_inversion[k,k]

							ParametersVariance[i,j,:,:] = numpy.diagonal(numpy.matrix(M_inversion_tmp).I).reshape(NumberOfBands,NumberOfParameters)
							M_inversion_tmp = None
			else:
				#ipshell = embed()
				# If there are no samples at all or there are samples but not prior, use only prior data
				Parameters[i,j,:,:] = PriorGapFiller.Parameters[i,j,:].reshape(NumberOfBands,NumberOfParameters)
				ParametersVariance[i,j,:,:] = PriorGapFiller.ParametersVariance[i,j,:].reshape(NumberOfBands,NumberOfParameters)

	#f = open('NIR.txt', 'a+')
	#f0, f1, f2 = Parameters[:,:,1,0][0][0], Parameters[:,:,1,1][0][0], Parameters[:,:,1,2][0][0]
	#NIR_BHR = f0 + (f1 * 0.189184) + (f2 * -1.377622)	
	#f.write(str(NIR_BHR) + '\n')
	#f.close()

	return Parameters, ParametersVariance, GoodnessOfFit


#--------------------------------------------------------------------------------#
from IPython import embed

strDoY = sys.argv[1]
DataDir = sys.argv[2]
strYear = sys.argv[3]
tile = sys.argv[4]

ProcessSnow = int( sys.argv[5] )

DataDir = DataDir + '/' + tile

print time.strftime("Processing starting at: %d/%m/%Y %H:%M:%S")
start = time.time()

# Set Prior directory based on the hostname
import socket
hostname = socket.gethostname()

#PriorDataDir = DataDir + '/Prior'
PriorDataDir = '/home/dn907640/MELODIES/data/MODIS/' + tile + '/Prior'

FileList, Year, DoY, JulianDoY, Weigth = GetFileList(strDoY, DataDir, int(strYear))

# From the first file get dimensions
TotalRows, TotalCols, NumberOfBands = GetDimensions(FileList[0])

NumberOfBands = 7
NumberOfParameters = 3

# Create arrays
Parameters = numpy.zeros((TotalRows, TotalCols, NumberOfBands, NumberOfParameters), numpy.float32)
ParametersVariance = numpy.zeros((TotalRows, TotalCols, NumberOfBands, NumberOfParameters), numpy.float32)
GoodnessOfFit = numpy.zeros((TotalRows, TotalCols), numpy.float32)
NumberOfSamples = numpy.zeros((TotalRows, TotalCols), numpy.float32)
NumberOfWeightedSamples = numpy.zeros((TotalRows, TotalCols), numpy.float32)

LengthOfInversionWindow = numpy.zeros((TotalRows, TotalCols), numpy.float32)

# Depending on the processing system, the composite could be created storing ALL
# datasets in RAM, however for prototyping a tile-based processing will be implemented.
# 100 tiles will be the default setting.
NumberOfTiles = 100
#NumberOfTiles = 1

#iRow = 1400
#iCol = 1000
#eRow = 1800
#eCol = 1400
# Input rows and cols must be in 1-based index
# To process the whole dataset eRow = TotalRows+1, eCol = TotalCols+1
iRow = 1
iCol = 1
eRow = 2401
eCol = 2401

rows = (eRow - iRow)
cols = (eCol - iCol)

for Tile in range(1,NumberOfTiles+1):

	InitRow = (Tile - 1) * (rows / NumberOfTiles) + (iRow - 1)
	EndRow = InitRow + (rows / NumberOfTiles)
	print InitRow, EndRow
	InitCol = (iCol - 1)
	print "Processing tile", Tile

	#Create temporal profile of matrices
	# M = Kernels^T C^-1 Kernels
	# V = Kernels^T C^-1 Reflectance
	# E = Reflectance^T C^-1 Reflectance
	NumberOfFiles = len(FileList)
	NumberOfRows = rows/NumberOfTiles
	NumberOfCols = cols
	M_profile = numpy.zeros((NumberOfRows, NumberOfCols, NumberOfBands*NumberOfParameters, NumberOfBands*NumberOfParameters, NumberOfFiles), numpy.float32)
	V_profile = numpy.zeros((NumberOfRows, NumberOfCols, NumberOfBands*NumberOfParameters, NumberOfFiles), numpy.float32)
	E_profile = numpy.zeros((NumberOfRows, NumberOfCols, NumberOfFiles), numpy.float32)

	tmpNumberOfSamples = numpy.zeros((NumberOfRows, NumberOfCols, NumberOfFiles), numpy.float32)
	tmpNumberOfWeightedSamples = numpy.zeros((NumberOfRows, NumberOfCols, NumberOfFiles), numpy.float32)
	tmpLengthOfInversionWindow = numpy.zeros((NumberOfRows, NumberOfCols), numpy.float32)

	NIR_Reflectance = numpy.zeros(((rows / NumberOfTiles), cols, NumberOfFiles), numpy.float32)
	
	FileNumber = 0
	for ReflectancesFile in FileList:
		StartReadingTime = time.time()

		print ReflectancesFile, Weigth[FileNumber]

		KernelsFile = ReflectancesFile[0:len(ReflectancesFile)-3] + "kernels.tif"
		Reflectance = GetReflectances(ReflectancesFile, KernelsFile, Weigth[FileNumber], InitRow, InitCol, 
                                      (rows / NumberOfTiles), cols, ProcessSnow)

		M_profile[:,:,:,:,FileNumber] = Reflectance.M * Weigth[FileNumber]
		V_profile[:,:,:,FileNumber] = Reflectance.V * Weigth[FileNumber]
		E_profile[:,:,FileNumber] = Reflectance.E * Weigth[FileNumber]

		tmpNumberOfSamples[:,:,FileNumber] = numpy.where( Reflectance.NumberOfSamples > 0.0 , 1., 0. )
		tmpNumberOfWeightedSamples[:,:,FileNumber] = Reflectance.NumberOfSamples

		# NIR band is store in band 2 (index 1)
		NIR_Reflectance[:,:,FileNumber] = Reflectance.Reflectance[:,:,1,0]

		Reflectance = None

		FileNumber += 1

		EndReadingTime = time.time()
		TimeElapsed = EndReadingTime - StartReadingTime
		print "Reading data time elapsed = ", (TimeElapsed)/60.0 , "minutes"

	print "Performing outlier detection..."
	# Get at least 7 observations within the 32 day full window
	MinNumberOfObs = 7

	for j in range(0,NIR_Reflectance.shape[1]):
		for i in range(0,NIR_Reflectance.shape[0]):
			# Extract temporal profile
			NIR_profile = NIR_Reflectance[i,j,:]
			# Perform outlier detection only if there are enough observations
			if NIR_profile.nonzero()[0].shape[0] >= MinNumberOfObs:
				#ipshell = embed()
				outlier_indices = GetOutlierIndices(NIR_profile, JulianDoY)
				if outlier_indices.shape[0] > 0:
					for index in outlier_indices:
						# Eliminate the observation from the matrices
						M_profile[i,j,:,:,index] = 0.0
						V_profile[i,j,:,index] = 0.0
						E_profile[i,j,index] = 0.0
						tmpNumberOfSamples[i,j,index] = 0.0
						tmpNumberOfWeightedSamples[i,j,index] = 0.0
						NIR_profile[index] = 0.0

	print "Get prior data..."
	Prior = GetPrior(PriorDataDir, strDoY, InitRow, InitCol, \
                     (rows / NumberOfTiles), cols, 2.0, ProcessSnow)
	# Get the prior to be used only as a gap filler
	PriorGapFiller = GetPrior(PriorDataDir, strDoY, InitRow, InitCol, \
                              (rows / NumberOfTiles), cols, 1.0, ProcessSnow)

	# Create accumulators
	M = numpy.sum(M_profile, axis=4)
	V = numpy.sum(V_profile, axis=3)
	E = numpy.sum(E_profile, axis=2)

	# Number of Samples
	tmpNumberOfWeightedSamples = numpy.sum(tmpNumberOfWeightedSamples, axis=2)
	tmpNumberOfSamples = numpy.sum(tmpNumberOfSamples, axis=2)

	# Clean temporal profiles
	M_profile = V_profile = E_profile = None

	# Extract min and max values from NIR_Reflectance
	indices = numpy.mgrid[0:NIR_Reflectance.shape[0], 0:NIR_Reflectance.shape[1]]
	NIR_Reflectance = numpy.ma.masked_equal(NIR_Reflectance, 0.0)
	indices_max = NIR_Reflectance.argmax(axis=2)
	indices_min = NIR_Reflectance.argmin(axis=2)
	
	NIR_ReflectanceStats = numpy.zeros((NumberOfRows, NumberOfCols, 2), numpy.float32)
	NIR_ReflectanceStats[:,:,0] = NIR_Reflectance[indices[0], indices[1], indices_max]	
	NIR_ReflectanceStats[:,:,1] = NIR_Reflectance[indices[0], indices[1], indices_min]
	NIR_Reflectance = None

	print "Performing BRDF model inversion..."

	tmpParameters, tmpParametersVariance, tmpGoodnessOfFit = \
        BRDF_Inverter(NIR_ReflectanceStats, M, V, E, \
                      Prior, PriorGapFiller, \
                      NumberOfBands, NumberOfParameters, tmpNumberOfSamples)

	#ipshell = embed()
	# Set NSamples = 0 when there is no prior information, samples are very likely to have very high uncert
	#tmpNumberOfSamples = numpy.where(Prior.Mask == 0, 0, tmpNumberOfSamples)

	Parameters[InitRow:EndRow, InitCol:InitCol+cols,:,:] = tmpParameters
	ParametersVariance[InitRow:EndRow,InitCol:InitCol+cols,:,:] = tmpParametersVariance
	GoodnessOfFit[InitRow:EndRow, InitCol:InitCol+cols] = tmpGoodnessOfFit
	NumberOfSamples[InitRow:EndRow,InitCol:InitCol+cols] = tmpNumberOfSamples
	NumberOfWeightedSamples[InitRow:EndRow,InitCol:InitCol+cols] = tmpNumberOfWeightedSamples
	LengthOfInversionWindow[InitRow:EndRow,InitCol:InitCol+cols] = tmpLengthOfInversionWindow

	tmpParameters = tmpParametersVariance = tmpNumberOfSamples \
    = tmpNumberOfWeightedSamples = tmpLengthOfInversionWindow = None

#exit()

print "Writing results to a file..."
#format = "GTiff"
format = "ENVI"
driver = gdal.GetDriverByName(format)
#new_dataset = driver.Create( 'BRDF_Parameters.'+ strYear + strDoY +'.img', TotalCols, TotalRows, (NumberOfBands*NumberOfParameters*2) + 2, GDT_Float32)
if ProcessSnow == 1:
	OutputFilename = 'BRDF_Parameters.' + strYear + strDoY + '.' + tile + '.Snow.img'
else:
	OutputFilename = 'BRDF_Parameters.' + strYear + strDoY + '.' + tile + '.img'

new_dataset = driver.Create( OutputFilename, TotalCols, TotalRows, \
                             (NumberOfBands*NumberOfParameters*2) + 3, \
                             GDT_Float32 )
                             #GDT_Float32, ['COMPRESS=PACKBITS'])

k = 1
for i in range(NumberOfBands):
	for j in range(NumberOfParameters):
		new_dataset.GetRasterBand(k).WriteArray(Parameters[:,:,i,j])
		new_dataset.GetRasterBand(k+(NumberOfBands*NumberOfParameters)).WriteArray(ParametersVariance[:,:,i,j])
		k += 1

new_dataset.GetRasterBand((NumberOfBands*NumberOfParameters*2) + 1).WriteArray(NumberOfSamples[:,:])
new_dataset.GetRasterBand((NumberOfBands*NumberOfParameters*2) + 2).WriteArray(NumberOfWeightedSamples[:,:])
new_dataset.GetRasterBand((NumberOfBands*NumberOfParameters*2) + 3).WriteArray(GoodnessOfFit[:,:])
new_dataset = None

print time.strftime("Processing finished at: %d/%m/%Y %H:%M:%S")
end = time.time()
print "Total time elapsed = ", (end - start)/3600.0, "hours =",  (end - start)/60.0 , "minutes"
