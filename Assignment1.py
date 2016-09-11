
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


LimitDepth = -1 # -1 corresponds to unbounded

if('-setfold' in sys.argv and '-depthOn' not in sys.argv and '-mf' not in sys.argv):
	## -- Just single training and test data for basic training -- ##
	if(len(trainFilehandle)==0):
		print "1.Training and test files not provided..... Exiting!!"
	else:
		ExampleDict = CreateExampleStruct(trainFilehandle[0:1])
		print ExampleDict
		if(test_index !=-1):
			TestDict = CreateTestStruct(open(sys.argv[test_index +1], 'r+'))
		Root = func.decideRoot(ExampleDict, GlobalAttrDict)
		gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, LimitDepth)
		sFlag = gRoot.ID3()
		depth = gRoot.getMaxDepth()
		print "Depth = ", depth
		y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
		if(test_index!=-1):
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			print len(y)




##--- For k fold validation
elif('-setfold' in sys.argv and '-depthOn' in sys.argv and foldValue > 1 and '-mf' not in sys.argv):
	print "Here"
	MaxAccuracy = 0.0
	AccuracyList = []
	hyperDepth = 0
	if(len(trainFilehandle) == 0):
		print "Training and test files not provided.... Exiting!!"
	else:
		for fixDepth in depthParam: ## this loop is for all the depths
			avgAccinDepth = 0
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
				print "Root: ", Root
				gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, fixDepth)
				sFlag = gRoot.ID3()
				depth = gRoot.getMaxDepth()
				print "Depth = ", depth
				y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
				y = func.Validate(gRoot, TestDict, TestDict['Result'])
				print "Y:" ,len(y)
				avgAccinDepth = avgAccinDepth + (float(len(ExampleDict['Result']) - len(y))/len(ExampleDict['Result']))*100
			locAcc = avgAccinDepth/foldValue		
			if(locAcc > MaxAccuracy) :
				MaxAccuracy = float(locAcc)
				hyperDepth = fixDepth
				
			AccuracyList.append(locAcc)
		print AccuracyList, MaxAccuracy, hyperDepth
		##---------- Now train on the selected hyper-parameter ---------------##
		ExampleDict = CreateExampleStruct(trainFilehandle)
		if(test_index != -1):
			TestDict = CreateTestStruct(open(sys.argv[test_index +1], 'r+'))
		Root = func.decideRoot(ExampleDict, GlobalAttrDict)
		gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0, hyperDepth)
		sFlag = gRoot.ID3()
		y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
		TrainingAccuracy = ((float(len(ExampleDict['Result']) - len(y)))/len(ExampleDict['Result']))*100
		print "Final Training Accuracy with hyper-parameter Depth = ",hyperDepth, "is ", TrainingAccuracy,"%"
		if(test_index != -1):
			y = func.Validate( gRoot, TestDict, TestDict['Result'])
			TestAccuracy = ((float(len(ExampleDict['Result']) - len(y)))/len(ExampleDict['Result']))*100
			print "Final Test Accuracy with hyper-parameter Depth = ",hyperDepth, "is ", TestAccuracy,"%"
			

##--- Setting C + K-fold
elif('-setfold' in sys.argv and '-depthOn' in sys.argv and foldValue > 1 and '-mf' in sys.argv):
	##--- Train with method-1
	HyperMethod = dict([])
	if(len(trainFilehandle)==0):
		print "Training and test files not provided... Exiting!!"
	else:
		##method-1: Majority feature value--
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
			print len(y), len(ExampleDict['Result'])
			avgAccMethod1 = avgAccMethod1 + (float(len(ExampleDict['Result']) - len(y))/len(ExampleDict['Result']))*100
		HyperMethod['Method1'] = avgAccMethod1/foldValue
 ##----------------------------------------------------------------------------------------------------------------------##
	##--- Train with method-2
	
		





				


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
	






