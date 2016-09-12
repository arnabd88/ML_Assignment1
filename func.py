##---------- Contains some utility functions ---------------##

import sys
import re
import copy
import math
import numpy


##---- Trims a string towards the left
def trimleft( trimString ):
	#trimString = trimString.split()
	while( re.match(' ',trimString)):
		trimString = trimString[1:]
	return trimString
	

##--- concats elements of list and returns a string ---##
def concatList(l1):
	l2 = ''
	if(len(l1)!=0):
		for i in l1:
			l2 = l2+i
	return l2

##--- trims all spaces from a string
def trimList( str1 ):
	l2 = ''
	for i in str1:
		if(i!=' '):
			l2 = l2+i
	return l2


def trimList( list1 ):
	l2 = []
	for i in list1:
		if(i != '' and i!='\n'):
			l2.append(i)
	return l2


def parseAttr(fattr):
    newAttr = 0
    AttrDict = dict(dict([]))
    AttrDict['_AttrOrder_'] = []
    for line in fattr:
		line = line.split('\n')[0]
		if(':' in line):
			Arg = line.split(':') ;
			Arg[1] = trimleft(Arg[1])
			label_list = Arg[1].split(',')
			label_dict = dict([])
			for i in range(0,len(label_list)):
				#label_dict[label_list[i].split('=')[0]] = label_list[i].split('=')[1]
				label_dict[label_list[i].split('=')[1]] = label_list[i].split('=')[0]
			AttrDict[Arg[0]] = label_dict
			if(Arg[0] != 'classes'):
				AttrDict['_AttrOrder_'].append(Arg[0])
    return AttrDict



	

#Entrophy return signature = [ 0_res, 1_res, Total, EntrophyValue ]

def Entrophy(Example, Attr):
	res = Attr['classes'].keys()
	LabelCount = 0.0;
	LabelCount_0_Count = 0.0;
	LabelCount_1_Count = 0.0;
	for i in Example['Result']:
		LabelCount = LabelCount + 1.0
		if( i== res[0]):
			LabelCount_0_Count = LabelCount_0_Count + 1.0 
		else:
			LabelCount_1_Count = LabelCount_1_Count + 1.0 
	if(LabelCount_1_Count == 0 or LabelCount_0_Count==0):
		Entr_S = 0
	else:
		Entr_S = -(LabelCount_0_Count/LabelCount)*numpy.log2(LabelCount_0_Count/LabelCount) - (LabelCount_1_Count/LabelCount)*numpy.log2(LabelCount_1_Count/LabelCount)
	return [LabelCount_0_Count, LabelCount_1_Count, LabelCount, Entr_S]


	

def getIG(Example, Attr, feat, Entrophy_S):
	AvgEnt = 0.0
	##localExampleDict = dict([])
	values_feat = Attr[feat].keys() 
	sampleExList = Example[feat]
	for v in values_feat:
		localExampleDict = dict([])
		localExampleDict['Result'] = []
		for i in range(0,len(sampleExList)):
			if( v == sampleExList[i]):
				localExampleDict['Result'].append(Example['Result'][i])
		tempEntrophyRet = Entrophy(localExampleDict, Attr);
		#print "            Entrophy for ",v ," = ", tempEntrophyRet
		AvgEnt = AvgEnt + (tempEntrophyRet[2]/len(sampleExList)) * tempEntrophyRet[3] 
	return (Entrophy_S - AvgEnt)
		
		
	


def decideRoot(ExampleDict, AttrDict):
	Features = AttrDict['_AttrOrder_']
	BestFeature = ''
	BestFeatureValue = 0
	E_S = Entrophy(ExampleDict, AttrDict)
	#print "Space Entrophy = ", E_S
	for feat in Features:
		#	print "     ~~~~~~~~~~~~ Feature = ", feat , "~~~~~~~~~~~~~~"
			IGv = getIG(ExampleDict, AttrDict, feat, E_S[3]);
		#	print "     ~~~~~~~~~~~~ IG = ", IGv, "~~~~~~~~~~~"
			if(IGv >= BestFeatureValue):
				BestFeatureValue = IGv ;
				BestFeature = feat ;
	return BestFeature



def Validate(dt,  vectDict, Result):
	testV = dict([])
	CollectResult = []
	for x in range(0,len(vectDict[vectDict.keys()[0]])):
		for w in range(0,len(vectDict.keys())):
			if(vectDict.keys()[w] != 'Result'):
				testV[vectDict.keys()[w]] = vectDict[vectDict.keys()[w]][x]

		pres = dt.predictResult(testV)
		if(pres != Result[x]):
			CollectResult.append(testV)
#	if(len(CollectResult) == 0):
#		print "Validation Successful: Accurate Prediction"
#	else:
#		print "Inaccuracy in Prediction"
	return CollectResult
