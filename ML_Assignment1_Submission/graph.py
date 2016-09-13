

import sys
import re
import copy
import func
import math
import numpy

class graph:

	def __init__ (self, Name, Type, Examples, Attr, CurrentDepth, limitDepth):
		self.name = Name
		self.Type = copy.deepcopy(Type)
		self.examples = copy.deepcopy(Examples)
		self.attr = Attr
		self.depth = copy.deepcopy(CurrentDepth)
		self.decision = dict([])
		self.limitDepth = limitDepth
		if(Type == 'leaf'):
			self.decision[self.name] = []




	def ExtractExSubset(self, examples, value):
			subExample = dict([])
			for j in examples.keys():
				if(j!=self.name):
					subExample[j] = []
					for i in range(0,len(examples[self.name])):
						if( examples[self.name][i]== value):
							subExample[j].append(examples[j][i])
			return subExample


				

	def ExtractAttrSubset(self, attr):
		subAttr = copy.deepcopy(attr)
		if(self.name in attr):
			del subAttr[self.name]
			subAttr['_AttrOrder_'].remove(self.name)
		return subAttr
		

	def getCommonLabel(self, examples):
		length = len(examples['Result'])
		res = examples['Result']
		lc0=0
		lc1=1
		for i in examples['Result']:
			if ( i == res[0] ):
				lc0 = lc0+1.0 
			else:
				lc1 = lc1+1.0
		if(lc0 >= lc1):
			return res[0]
		else:
			return res[1]


	def ID3(self):
		#print "Run-ID3"
		res = self.attr['classes'].keys()
		##nd = dict([])
		if (not( res[0] in self.examples['Result'] and res[1] in self.examples['Result'])):
			if(res[0] in self.examples['Result']):
				self.decision[res[0]] = []
			else:
				self.decision[res[1]] = []
			#self.decision.append(nd)
			self.Type = 'leaf'
			#print "Early return"
			return 1
		else:
			##----- Loope over all the features and create a decision node -----
			self.Values = self.attr[self.name].keys()
			subAttr     = self.ExtractAttrSubset(self.attr)
			for v in self.Values:
				subExample = self.ExtractExSubset(self.examples, v)
				if(len(subExample['Result']) == 0): # no input available
					MaxLabel = self.getCommonLabel(self.examples)
					gnext = graph(MaxLabel, 'leaf', subExample, subAttr, self.depth+1, self.limitDepth)
					#print "My-Depth = ",self.depth ,"  |  Child-Depth = ", self.depth+1, "  MaxLabel = ", MaxLabel
					self.decision[v] = [MaxLabel,gnext]
					#self.decision.append(nd)
				else:
					nextNode   = func.decideRoot(subExample, subAttr)
					#print nextNode
					if(self.depth+1 == self.limitDepth):
						MaxLabel = self.getCommonLabel(subExample)
						gnext    = graph(MaxLabel, 'leaf', subExample, subAttr, self.depth+1, self.limitDepth)
						self.decision[v] = [MaxLabel, gnext]
					else:
						gnext      = graph(nextNode, 'internal', subExample, subAttr, self.depth+1, self.limitDepth)
						#print "My-Depth = ",self.depth ,"  |  Child-Depth = ", self.depth+1, "  nextNode = ", nextNode, "V =", v
						self.decision[v] = [nextNode,gnext]
						#self.decision.append()
						succ       = gnext.ID3()
			#self.decision.append(nd)
		return 1
			
		


	def predictResult(self, testV):
		#print testV
		#print self.name
		#print self.decision
		#print self.name
		if( self.Type=='leaf' and len(self.decision.keys())==1 ):
			return self.decision.keys()[0]
		else :		
			return self.decision[testV[self.name]][1].predictResult(testV)

	def getMaxDepth(self):
		depth = 0
		if( self.Type=='leaf'):
			return self.depth
		else:
			for kc, child in self.decision.iteritems():
				d = child[1].getMaxDepth()
				if(d > depth):
					depth = d
		return depth
