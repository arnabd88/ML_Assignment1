
## python thisFile.py -fold <foldValue> <trainingData1> .... <trainingDatak>  -test <test data> -Attr <ElabAttrFile>

import sys
import re
import copy
import func
import graph
import math
import numpy



	

#Entrophy return signature = [ 0_res, 1_res, Total, EntrophyValue ]


fold_index = -1
test_index = -1
attr_index = -1
foldValue = 0

depthParam = [1, 2, 3, 4, 5, 10, 15, 20]
verbose=-1
if ('-Attr' in sys.argv):
	attr_index = sys.argv.index('-Attr')
else:
	print 'Pass the Attr file correctly... Exiting!!'
	exit
if ('-fold' in sys.argv):
	fold_index = sys.argv.index('-fold')
if ('-test' in sys.argv):
	test_index = sys.argv.index('-test')
if ('-verbose' in sys.argv):
	verbose = 1

##-- Get the inorder attribute List --##
fattr = open(sys.argv[attr_index+1], 'r+')

GlobalAttrDict = func.parseAttr(fattr)
if(verbose==1):
	print "<=========== Printing the Global Attributes data structure ==============>"
	for i,v in GlobalAttrDict.iteritems():
		print i, v
print "<========================================================================>"

def CreateExampleStruct(FileList):
	exDict = dict([])
	exList = []
	FileList_buf = copy.deepcopy(FileList)
	for i in range(0,len(FileList)):
		for j in FileList[i]:
			dataList = j.split('\n')[0].split(',')
			exList.append(dataList)

	FeatureOrder = GlobalAttrDict['_AttrOrder_']
	for k in range(0,len(FeatureOrder)):
		tl = []
		for row in exList:
			tl.append(row[k])
		exDict[FeatureOrder[k]] = tl
	res = []
	for row in exList:
		res.append(row[len(FeatureOrder)])
	exDict['Result'] = res
		
			
	#print "ExList: " , exList
#	for k in range(0,len(FeatureOrder)):
#		tl = [row[k] for row in exList]
#		exDict[FeatureOrder[k]] = tl
#		exDict['Result'] = [row[len(FeatureOrder)] for row in exList]
#	print exDict
	return exDict


def CreateTestStruct(FilePtr):
	return CreateExampleStruct([FilePtr])
	
	



trainFilehandle = []
if(fold_index != -1):
	foldValue = int(sys.argv[fold_index + 1])
	for f in range(1,int(sys.argv[fold_index + 1 ])+1):
		trainFilehandle.append(open(sys.argv[fold_index+1 + f], 'r+').read().splitlines())
##	ExampleDict = CreateExampleStruct(trainFilehandle)
	

##--------------------- Create the Example DataStructure -----------------##
#GlobalExample = [] ## have type of dict([])
#if(fold_index != -1):
#	for f in range(1,int(sys.argv[fold_index + 1 ])+1):
#		fopen = open(sys.argv[fold_index+1 + f], 'r+')
#		exList = []
#		for i in fopen:
#			dataList = i.split('\n')[0].split(',')
#			exList.append(dataList)
#		GlobalExample.append(exList)



##------------------- Create the Test Datastructure ---------------------##
#TestDict = dict([])
#TestDict['Result'] = []
#if(test_index != -1):
#	ftest = open(sys.argv[test_index + 1], 'r+')
#	exList = []
#	for i in ftest:
#		dataList = i.split('\n')[0].split(',')
#		exList.append(dataList)
#
#	TestFeatureOrder = GlobalAttrDict['_AttrOrder_']
#	for k in range(0,len(TestFeatureOrder)):
#		tl = [row[k] for row in exList]
#		TestDict[TestFeatureOrder[k]] = tl
#		TestDict['Result'] = [row[len(TestFeatureOrder)] for row in exList]


##------------------ Train and test on the Training Data ---------------##



def getSdMean( acclist  ):
	if(len(acclist)==0):
		return []
	else:
		resultList = []
		partSum = 0
		for i in acclist:
			partSum = partSum + i
		mean = float(partSum)/len(acclist)
		resultList.append(mean)
		##-- Find the SD --
		sumSD = 0
		for i in acclist:
			sumSD = sumSD + (i-mean)**2
		SD = math.sqrt(float(sumSD)/len(acclist))
		resultList.append(SD)
	return resultList


LimitDepth = -1 # -1 corresponds to unbounded

if('-setfold' in sys.argv and '-depthOn' not in sys.argv and '-mf' not in sys.argv):
	## -- Just single training and test data for basic training -- ##
	if(len(trainFilehandle)==0):
		print "1.Training and test files not provided..... Exiting!!"
	else:
		ExampleDict = CreateExampleStruct(trainFilehandle[0:1])
		#print ExampleDict
		if(test_index !=-1):
			TestDict = CreateTestStruct(open(sys.argv[test_index +1], 'r+'))
		Root = func.decideRoot(ExampleDict, GlobalAttrDict)
		gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, LimitDepth)
		sFlag = gRoot.ID3()
		depth = gRoot.getMaxDepth()
		print "MaxDepth of the Tree= ", depth
		y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
		print "Training Accuracy = ", float(len(ExampleDict['Result']) - len(y))/len(ExampleDict['Result']),"%"
		if(test_index!=-1):
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print "Test Accuracy = ", float(len(TestDict['Result']) - len(y))/len(TestDict['Result']),"%"
			#print len(y)
		print "\n\n"




##--- For k fold validation
elif('-setfold' in sys.argv and '-depthOn' in sys.argv and foldValue > 1 and '-mf' not in sys.argv):
	print "Here"
	MaxAccuracy = 0.0
	#AccuracyList = []
	hyperDepth = 0
	if(len(trainFilehandle) == 0):
		print "Training and test files not provided.... Exiting!!"
	else:
		SD_Mean_Tracker = []     ##--- Tracks the mean and accuracy for each depth
		print "*** Starting K-fold cross Validation with depth as Hyper ***\n"
		for fixDepth in depthParam: ## this loop is for all the depths
			avgAccinDepth = 0
			AccuracyTracker = [] ##--- Collect the accuracy at each fold per depth
			for it in range(0,foldValue):
				TrainingFileList = []
				ExampleDict = dict([])
				TestDict = dict([])
				#TestDict    = CreateTestStruct(trainFilehandle[it])
				TestDict    = CreateExampleStruct([trainFilehandle[it]])
				for el in range(0,foldValue):
					if(el !=it):
						TrainingFileList.append(trainFilehandle[el])
				ExampleDict = CreateExampleStruct(TrainingFileList)
				Root = func.decideRoot(ExampleDict, GlobalAttrDict)
				print "Current iteration Root: ", Root
				print "Fixed Depth Limit: ", fixDepth
				gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, fixDepth)
				sFlag = gRoot.ID3()
				depth = gRoot.getMaxDepth()
				print "Tree Depth = ", depth ,"\n"
				y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
				y = func.Validate(gRoot, TestDict, TestDict['Result'])
				#print "Y:" ,len(y)
				avgAccinDepth = avgAccinDepth + (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
				AccuracyTracker.append((float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100)
			SD_Mean_Tracker.append(getSdMean(AccuracyTracker))
			locAcc = avgAccinDepth/foldValue		
			if(locAcc > MaxAccuracy) :
				MaxAccuracy = float(locAcc)
				hyperDepth = fixDepth
		print "*** K-Fold cross Validation Ends ******************************\n"
		print "--------------- K-Fold Experiment Result Detail ---------------------"
		for d in range(0,len(depthParam)):
			print "At Depth Limit:", depthParam[d], "    Average-Accuracy:", SD_Mean_Tracker[d][0],"%     Standard-Deviation:", SD_Mean_Tracker[d][1]
		print "---------------------------------------------------------------------\n\n"
		print "Selected-Hyper-Depth = ", hyperDepth, "\n"
				
		#	AccuracyList.append(locAcc)
		#print AccuracyList, MaxAccuracy, hyperDepth
		print "##---------- Now train on the selected hyper-parameter ---------------##"
		ExampleDict = CreateExampleStruct(trainFilehandle)
		if(test_index != -1):
			TestDict = CreateTestStruct(open(sys.argv[test_index +1], 'r+'))
		Root = func.decideRoot(ExampleDict, GlobalAttrDict)
		gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, hyperDepth)
		sFlag = gRoot.ID3()
		y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
		TrainingAccuracy = ((float(len(ExampleDict['Result']) - len(y)))/len(ExampleDict['Result']))*100
		print "Final Training Accuracy with hyper-parameter Depth = ",hyperDepth, "is ", TrainingAccuracy,"%\n\n"
		if(test_index != -1):
			print "------------ Testing with Test Data in current Setting -----------"
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			TestAccuracy = ((float(len(TestDict['Result']) - len(y)))/len(TestDict['Result']))*100
			print "Final Test Accuracy with hyper-parameter Depth = ",hyperDepth, "is ", TestAccuracy,"%\n\n"
			

##--- Setting C + K-fold
elif('-setfold' in sys.argv and foldValue > 1 and '-mf' in sys.argv):
	##--- Train with method-1
	HyperMethod = dict([])
	if(len(trainFilehandle)==0):
		print "Training and test files not provided... Exiting!!"
	else:
		Method_SD_Tracker = []  #--- MEthod-1, MEthod2, Method3 tracker for SD and Mean
		##method-1: Majority feature value--
		print "~~~~~~~~~~~~~~~~ Starting Training Method-I ~~~~~~~~~~~~~~~~~~~~~~~~"
		ExampleDict = CreateExampleStruct(trainFilehandle)
		localAttrStruct = copy.deepcopy(GlobalAttrDict)
		FeatureAttr = dict([])
		for atr in localAttrStruct['_AttrOrder_']:
			if('?' in ExampleDict[atr]):  ##missing Feature value
				##-- Find the majority feature value for this attribute
				valA = localAttrStruct[atr].keys()
				MaxCount = 0;
				BestFeature = ''
				for v in valA:
					count = 0
					for k in ExampleDict[atr]:
						if(v==k):
							count = count + 1.0
					if(count > MaxCount):
						MaxCount = count
						BestFeature = v
				FeatureAttr[atr] = v
	
		avgAccMethod1 = 0	
		AccucracyTracker = []
		for it in range(0,foldValue):
			TrainingFileList = []
			ExampleDict = dict([])
			TestDict    = dict([])
			for el in range(0,foldValue):
				if(el != it):
					TrainingFileList.append(trainFilehandle[el])
			ExampleDict = CreateExampleStruct(TrainingFileList)
			TestDict = CreateExampleStruct([trainFilehandle[it]])
			##---- Set the missing feature value derived earlier ----##
			for atr in FeatureAttr.keys():
				for items in range(0,len(ExampleDict[atr])):
					if( ExampleDict[atr][items] == '?'):
						ExampleDict[atr][items] = FeatureAttr[atr]
				for items in range(0,len(TestDict[atr])):
					if( TestDict[atr][items] == '?'):
						TestDict[atr][items] = FeatureAttr[atr]
			Root = func.decideRoot(ExampleDict, GlobalAttrDict)
			gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, -1)
			sFlag = gRoot.ID3()
			y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print len(y), len(TestDict['Result'])
			avgAccMethod1 = avgAccMethod1 + (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
			AccucracyTracker.append((float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100)
		HyperMethod['Method1'] = avgAccMethod1/foldValue
		Method_SD_Tracker.append(getSdMean(AccucracyTracker))
		print "Method-I = ", HyperMethod['Method1']
 ##----------------------------------------------------------------------------------------------------------------------##
##		##--- Train with method-3 -> Treat the missing feature as special feature: requires update to the attribute table
##		print "~~~~~~~~~~~~~~~~ Starting Training Method-III ~~~~~~~~~~~~~~~~~~~~~~~"
##		ExampleDict = CreateExampleStruct(trainFilehandle)
##		localAttrStr = copy.deepcopy(GlobalAttrDict)
##		for atr in localAttrStr['_AttrOrder_']:
##			if( '?' in ExampleDict[atr]):  ## detecting the missing feature value
##				if( '?' not in localAttrStr[atr].keys()):
##					localAttrStr[atr]['?'] = 'Special'
##		
##		avgAccMethod3 = 0	
##		for it in range(0,foldValue):
##			TrainingFileList = []
##			ExampleDict = dict([])
##			TestDict    = dict([])
##			for el in range(0,foldValue):
##				TrainingFileList.append(trainFilehandle[el])
##			ExampleDict = CreateExampleStruct(TrainingFileList)
##			TestDict    = CreateExampleStruct([trainFilehandle[it]])
##			Root = func.decideRoot(ExampleDict, localAttrStr)
##			gRoot = graph.graph( Root, 'ROOT', ExampleDict, localAttrStr, 0, -1)
##			sFlag = gRoot.ID3()
##			y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
##			y = func.Validate( gRoot, TestDict, TestDict['Result'])
##			print len(y), len(TestDict['Result'])
##			avgAccMethod3 = avgAccMethod3 + (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
##		HyperMethod['Method3'] = avgAccMethod3/foldValue
##		print "Method-III = ", HyperMethod['Method3']
			
 ##----------------------------------------------------------------------------------------------------------------------##
		##--- Train with method-2
		print "~~~~~~~~~~~~~~~~ Starting Training Method-II ~~~~~~~~~~~~~~~~~~~~~~~~"
		ExampleDict = CreateExampleStruct(trainFilehandle)
		localAttrStruct = copy.deepcopy(GlobalAttrDict)
		trackPartition = []
		for atr in localAttrStruct['_AttrOrder_']:
			if('?' in ExampleDict[atr]):  ##missing feature value
				for el in range(0,len(ExampleDict[atr])):
					if( ExampleDict[atr][el] == '?' ):
						clabel = ExampleDict['Result'][el]
						MaxCount = 0
						BestFeature = ''
						for v in localAttrStruct[atr].keys():
							count = 0
							for j in range(0,len(ExampleDict[atr])):
								if(ExampleDict[atr][j] != '?' and ExampleDict['Result'][j]==clabel):
									count = count + 1.0
							if(count > MaxCount):
								MaxCount = count
								BestFeature = v
						ExampleDict[atr][el] = BestFeature
		CorrectedExample = copy.deepcopy(ExampleDict)
		##----- Manage the partitions -------##
		for eachList in trainFilehandle:
			trackPartition.append(len(eachList))
		if(len(trackPartition) != foldValue):
			print "Partition List does not corresponds with foldValue ...FATAL.. Exiting!!"
		avgAccMethod2 = 0
		AccucracyTracker = []
		for it in range(0,foldValue):
			##---- Create the Example and Test set
			tempExDict = dict([])	
			tempTestDict = dict([])
			tempList = []
			avoidFrom = 0
			avoidTill = 0
			detectAvoid = 0
			print trackPartition
			for i in range(0,len(trackPartition)):
				if(i!=it and detectAvoid==0):
					avoidFrom = avoidFrom + trackPartition[i]
				elif(i==it and detectAvoid==0):
					avoidTill = avoidFrom + trackPartition[i]-1
					detectAvoid = 1
			#print "IT = ", it, "AvoidFrom = ", avoidFrom, "avoidTill =", avoidTill
			for k in ExampleDict.keys():   ##--- Partition the Example and Test Dict from the total Set
				tempTestDict[k] = []
				tempExDict[k] = []
				for el in range(0,len(ExampleDict[k])):
					if( el >= avoidFrom and el <=avoidTill ):
						tempTestDict[k].append(ExampleDict[k][el])
					else:
						tempExDict[k].append(ExampleDict[k][el])
			Root = func.decideRoot(tempExDict, GlobalAttrDict)
			gRoot = graph.graph(Root, 'ROOT', tempExDict, GlobalAttrDict, 0, -1)
			sFlag = gRoot.ID3()
			y = func.Validate( gRoot, tempExDict, tempExDict['Result'] )
			y = func.Validate( gRoot, tempTestDict, tempTestDict['Result'] )
			print len(y), len(tempTestDict['Result'])
			avgAccMethod2 = avgAccMethod2 + (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
			AccucracyTracker.append((float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100)
		Method_SD_Tracker.append(getSdMean(AccucracyTracker))
		HyperMethod['Method2'] = avgAccMethod2/foldValue
		print "Method-II = ", HyperMethod['Method2']

 ##----------------------------------------------------------------------------------------------------------------------##
		##--- Train with method-3 -> Treat the missing feature as special feature: requires update to the attribute table
		print "~~~~~~~~~~~~~~~~ Starting Training Method-III ~~~~~~~~~~~~~~~~~~~~~~~"
		ExampleDict = CreateExampleStruct(trainFilehandle)
		localAttrStr = copy.deepcopy(GlobalAttrDict)
		for atr in localAttrStr['_AttrOrder_']:
			if( '?' in ExampleDict[atr]):  ## detecting the missing feature value
				if( '?' not in localAttrStr[atr].keys()):
					localAttrStr[atr]['?'] = 'Special'
		
		avgAccMethod3 = 0	
		AccucracyTracker = []
		for it in range(0,foldValue):
			TrainingFileList = []
			ExampleDict = dict([])
			TestDict    = dict([])
			for el in range(0,foldValue):
				TrainingFileList.append(trainFilehandle[el])
			ExampleDict = CreateExampleStruct(TrainingFileList)
			TestDict    = CreateExampleStruct([trainFilehandle[it]])
			Root = func.decideRoot(ExampleDict, localAttrStr)
			gRoot = graph.graph( Root, 'ROOT', ExampleDict, localAttrStr, 0, -1)
			sFlag = gRoot.ID3()
			y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print len(y), len(TestDict['Result'])
			avgAccMethod3 = avgAccMethod3 + (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
			AccucracyTracker.append((float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100)
		Method_SD_Tracker.append(getSdMean(AccucracyTracker))
		HyperMethod['Method3'] = avgAccMethod3/foldValue
		print "Method-III = ", HyperMethod['Method3']

		WhoWon = ''
		MaxVal = 0
		for i in HyperMethod.keys():
			if(HyperMethod[i] >= MaxVal):
				WhoWon = i
				MaxVal = HyperMethod[i]

		##-------------- Retraining ------------------##

		if( WhoWon == 'Method1'):
			print 'Method1 Won - Train Full data using Method1 and Test'
			ExampleDict = CreateExampleStruct(trainFilehandle)
			if(test_index != -1):
				TestDict = CreateTestStruct(open(sys.argv[test_index + 1], 'r+'))
			localAttrStruct = copy.deepcopy(GlobalAttrDict)
			FeatureAttr = dict([])
			##----- Find the Best Feature for training set -----##
			for atr in localAttrStruct['_AttrOrder_']:
				if('?' in ExampleDict[atr]):
					valA = localAttrStruct[atr].keys()
					MaxCount = 0
					BestFeature = ''
					for v in valA:
						count = 0
						for k in ExampleDict[atr]:
							if(v==k):
								count = count + 1.0
						if(count > MaxCount):
							MaxCount = count
							BestFeature = v
					for el in range(0,len(ExampleDict[atr])):
						if(ExampleDict[atr][el] == '?'):
							ExampleDict[atr][el] = BestFeature
			##----- Find the Best Feature for test set -----##
			for atr in localAttrStruct['_AttrOrder_']:
				if('?' in TestDict[atr]):
					valA = localAttrStruct[atr].keys()
					MaxCount = 0
					BestFeature = ''
					for v in valA:
						count = 0
						for k in TestDict[atr]:
							if(v==k):
								count = count + 1.0
						if(count > MaxCount):
							MaxCount = count
							BestFeature = v
					for el in range(0,len(TestDict[atr])):
						if(TestDict[atr][el] == '?'):
							TestDict[atr][el] = BestFeature
			Root = func.decideRoot(ExampleDict, GlobalAttrDict)
			gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, -1)
			sFlag = gRoot.ID3()
			y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
			print 'TrainingAccuracy in M1 = ', (float(len(ExampleDict['Result']) - len(y))/len(ExampleDict['Result']))*100
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print len(y), len(TestDict['Result'])
			print 'TestAccuracy in M1 = ', (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
			
		elif(WhoWon == 'Method2'):
			print 'Method2 Won - Train Full data using Method2 and Test'
			ExampleDict = CreateExampleStruct(trainFilehandle)
			localAttrStruct = copy.deepcopy(GlobalAttrDict)
			for atr in localAttrStruct['_AttrOrder_']:
				if ('?' in ExampleDict[atr]):
					for el in range(0,len(ExampleDict[atr])):
						if( ExampleDict[atr][el] == '?' ):
							clabel = ExampleDict['Result'][el]
							MaxCount = 0;
							BestFeature = ''
							for v in localAttrStruct[atr].keys():
								count = 0
								for j in range(0,len(ExampleDict[atr])):
									if( ExampleDict[atr][j] != '?' and ExampleDict['Result'][j]==clabel):
										count = count + 1.0
								if(count > MaxCount):
									MaxCount = count
									BestFeature = v
							ExampleDict[atr][el] = BestFeature
			CorrectedExample = copy.deepcopy(ExampleDict)
			##---- Correct the test data as method1 to remove any bias ----
			TestDict = CreateTestStruct(open(sys.argv[test_index + 1], 'r+'))
			for atr in localAttrStruct['_AttrOrder_']:
				if('?' in TestDict[atr]):
					valA = localAttrStruct[atr].keys()
					MaxCount = 0
					BestFeature = ''
					for v in valA:
						count = 0
						for k in TestDict[atr]:
							if(v==k):
								count = count + 1.0
						if(count > MaxCount):
							MaxCount = count
							BestFeature = v
					for el in range(0,len(TestDict[atr])):
						if(TestDict[atr][el] == '?'):
							TestDict[atr][el] = BestFeature
			##----- Start Training ------#####
			Root = func.decideRoot(ExampleDict, localAttrStruct)
			gRoot = graph.graph(Root, 'ROOT', ExampleDict, localAttrStruct, 0, -1)
			sFlag = gRoot.ID3()
			y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
			print 'TrainingAccuracy in M2 = ', (float(len(ExampleDict['Result']) - len(y))/len(ExampleDict['Result']))*100
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print "OK: ", len(y), len(TestDict['Result'])
			print 'TestAccuracy in M2 = ', (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
			

			
		elif(WhoWon == 'Method3'):
			print 'Method3 Won - Train Full data using Method3 and Test'
			ExampleDict = CreateExampleStruct(trainFilehandle)
			localAttrStr = copy.deepcopy(GlobalAttrDict)
			for atr in localAttrStr['_AttrOrder_']:
				if( '?' in ExampleDict[atr]):
					if( '?' not in localAttrStr[atr].keys()):
						localAttrStr[atr]['?'] = 'Special'
			TestDict = CreateTestStruct(open(sys.argv[test_index + 1], 'r+'))
			Root = func.decideRoot(ExampleDict, localAttrStr)
			gRoot = graph.graph( Root, 'ROOT', ExampleDict, localAttrStr, 0, -1)
			sFlag = gRoot.ID3()
			depth = gRoot.getMaxDepth()
			y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
			print 'TrainingAccuracy in M3 = ', (float(len(ExampleDict['Result']) - len(y))/len(ExampleDict['Result']))*100
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print "OK3: ", len(y), len(TestDict['Result'])
			print 'TestAccuracy in M3 = ', (float(len(TestDict['Result']) - len(y))/len(TestDict['Result']))*100
			
		else:
			print 'Something is Wrong'







		
				
			
							
	
		





				


else:
	print "HelloHere"
	print foldValue




#for i in range(0,len(GlobalExample)):
#	##---- Make the example as a dictionary of attr -> values
#	Example = GlobalExample[i]
#	FeatureOrder = GlobalAttrDict['_AttrOrder_']
#	ExampleDict = dict([])
#	#for j in range(0, len(Example)):
#	for k in range(0,len(FeatureOrder)):
#		tl = [row[k] for row in Example]
#		ExampleDict[FeatureOrder[k]] = [row[k] for row in Example]
#	ExampleDict['Result'] = [row[len(FeatureOrder)] for row in Example]
#	Root = func.decideRoot(ExampleDict, GlobalAttrDict)
#	gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0) ## create root node
#	successFlag = gRoot.ID3()  ## create graph
#	depth = gRoot.getMaxDepth()
#	print "Depth = ", depth ,"\n\n"  ## report the tree depth
#	print"##--------- CrossCheck the Training Data : Create Test Vectors -----------##"
#	y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
#	if(test_index != -1):
#		print "##-------- Validating prediction for Test Data -----------##"
#		y = func.Validate( gRoot, TestDict, TestDict['Result'] )
#		print len(y)
#		print len(ExampleDict[ExampleDict.keys()[0]])
	






