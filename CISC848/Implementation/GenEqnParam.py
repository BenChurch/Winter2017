import csv
import numpy as np
from scipy.optimize import minimize

AllOriginalParams = [0.6, 0.4, 1.5, 10.41, 20, 0, 1.176, 0.395, 0.646, 1, 0.35, 0.61, 0.71, 0.54, 0.56, 0.704, 0, 0.275, 0.66, 0, 0.275, 0.66, 0, 0.275, 0.66]

# Following subsets of parameters are subject to internal ordering constraints
avParams = [0.395, 0.646, 1.0]
acParams = [0.35, 0.61, 0.71]
auParams = [0.45, 0.56, 0.704]

confParams = [0, 0.275, 0.66]
integParams = [0, 0.275, 0.66]
availParams = [0, 0.275, 0.66]

# Used just for iteration enumeration, new param values stored in other variables
ParamSets = [avParams, acParams, auParams, confParams, integParams, availParams]

SearchSpace = np.linspace(0,1,10)
for MaxParam in SearchSpace:
  for Param in enumerate(ParamSets):
    Param[2] = MaxParam

"""
BaseScore6 = round_to_1_decimal(((0.6*Impact)+(0.4*Exploitability)–1.5)*f(Impact))
Impact = 10.41*(1-(1-ConfImpact)*(1-IntegImpact)*(1-AvailImpact))
Exploitability = 20* AccessVector*AccessComplexity*Authentication
f(impact)= 0 if Impact=0, 1.176 otherwise
AccessVector = case AccessVector of
 requires local access: 0.395
 adjacent network accessible: 0.646
 network accessible: 1.0
AccessComplexity = case AccessComplexity of
 high: 0.35
 medium: 0.61
 low: 0.71
Authentication = case Authentication of
 requires multiple instances of authentication: 0.45
 requires single instance of authentication: 0.56
 requires no authentication:  0.704
ConfImpact = case ConfidentialityImpact of
 none: 0.0
 partial: 0.275
 complete: 0.660
IntegImpact = case IntegrityImpact of
 none: 0.0
 partial: 0.275
 complete: 0.660
AvailImpact = case AvailabilityImpact of
 none: 0.0
 partial: 0.275
 complete: 0.660
"""