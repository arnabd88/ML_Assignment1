
## python thisFile.py -fold <foldValue> <trainingData1> .... <trainingDatak>  -test <test data> -Attr <ElabAttrFile>

import sys
import re
import copy
import func
import graph
import math
import numpy



	

#Entrophy return signature = [ 0_res, 1_res, Total, EntrophyValue ]

##def Entrophy(Example, Attr):
##	res = Attr['classes'].keys()
##	LabelCount = 0.0;
##	LabelCount_0_Count = 0.0;
##	LabelCount_1_Count = 0.0;
##	for i in Example['Result']:
##		LabelCount = LabelCount + 1.0
##		if( i== res[0]):
##			LabelCount_0_Count = LabelCount_0_Count + 1.0 
##		else:
##			LabelCount_1_Count = LabelCount_1_Count + 1.0 
##	if(LabelCount_1_Count == 0 or LabelCount_0_Count==0):
##		Entr_S = 0
##	else:
##		Entr_S = -(LabelCount_0_Count/LabelCount)*numpy.log2(LabelCount_0_Count/LabelCount) - (LabelCount_1_Count/LabelCount)*numpy.log2(LabelCount_1_Count/LabelCount)
##	return [LabelCount_0_Count, LabelCount_1_Count, LabelCount, Entr_S]
##
##
##	
##
##def getIG(Example, Attr, feat, Entrophy_S):
##	print "IGain"
##	AvgEnt = 0.0
##	##localExampleDict = dict([])
##	values_feat = Attr[feat].keys() 
##	sampleExList = Example[feat]
##	for v in values_feat:
##		localExampleDict = dict([])
##		localExampleDict['Result'] = []
##		for i in range(0,len(sampleExList)):
##			if( v == sampleExList[i]):
##				localExampleDict['Result'].append(Example['Result'][i])
##		tempEntrophyRet = Entrophy(localExampleDict, Attr);
##		AvgEnt = AvgEnt + (tempEntrophyRet[2]/len(sampleExList)) * tempEntrophyRet[3] 
##	return (Entrophy_S - AvgEnt)
##		
##		
##	
##
##
##def decideRoot(ExampleDict, AttrDict):
##	Features = AttrDict['_AttrOrder_']
##	BestFeature = ''
##	BestFeatureValue = 0
##	E_S = Entrophy(ExampleDict, AttrDict)
##	print "Space Entrophy = ", E_S
##	for feat in Features:
##			print "Feature = ", feat
##			IGv = getIG(ExampleDict, AttrDict, feat, E_S[3]);
##			print "IG = ", IGv
##			if(IGv > BestFeatureValue):
##				BestFeatureValue = IGv ;
##				BestFeature = feat ;
##	return BestFeature
##


fold_index = -1
test_index = -1
attr_index = -1
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

##--------------------- Create the Example DataStructure -----------------##
trainFileHandle = []
GlobalExample = [] ## have type of dict([])
if(fold_index != -1):
	for f in range(1,int(sys.argv[fold_index + 1 ])+1):
		fopen = open(sys.argv[fold_index+1 + f], 'r+')
		exList = []
		for i in fopen:
			dataList = i.split('\n')[0].split(',')
			exList.append(dataList)
		GlobalExample.append(exList)



##------------------- Create the Test Datastructure ---------------------##
TestDict = dict([])
TestDict['Result'] = []
if(test_index != -1):
	ftest = open(sys.argv[test_index + 1], 'r+')
	exList = []
	for i in ftest:
		dataList = i.split('\n')[0].split(',')
		exList.append(dataList)

	TestFeatureOrder = GlobalAttrDict['_AttrOrder_']
	for k in range(0,len(TestFeatureOrder)):
		tl = [row[k] for row in exList]
		TestDict[TestFeatureOrder[k]] = tl
		TestDict['Result'] = [row[len(TestFeatureOrder)] for row in exList]


##------------------ Train and test on the Training Data ---------------##
for i in range(0,len(GlobalExample)):
	##---- Make the example as a dictionary of attr -> values
	Example = GlobalExample[i]
	FeatureOrder = GlobalAttrDict['_AttrOrder_']
	ExampleDict = dict([])
	#for j in range(0, len(Example)):
	for k in range(0,len(FeatureOrder)):
		tl = [row[k] for row in Example]
		ExampleDict[FeatureOrder[k]] = [row[k] for row in Example]
	ExampleDict['Result'] = [row[len(FeatureOrder)] for row in Example]
	Root = func.decideRoot(ExampleDict, GlobalAttrDict)
	##---------- Create the root node -------------##
	gRoot = graph.graph(Root, 'ROOT', ExampleDict, GlobalAttrDict, 0)
	##---------- Create the graph -----------------##
	successFlag = gRoot.ID3()
	##------- Finished cross-checking Training Data ------------##
	depth = gRoot.getMaxDepth()
	print "##------- Reporting Tree Depth ----------------------------##"
	print "Depth = ", depth ,"\n\n"
	print"##--------- CrossCheck the Training Data : Create Test Vectors -----------##"
	y = func.Validate( gRoot, ExampleDict, ExampleDict['Result'])
	if(test_index != -1):
		print "##-------- Validating prediction for Test Data -----------##"
		y = func.Validate( gRoot, TestDict, TestDict['Result'] )
		print len(y)
		print len(ExampleDict[ExampleDict.keys()[0]])
	






