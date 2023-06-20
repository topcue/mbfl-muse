#!/usr/bin/python2.7

"""Turns a coverage/kill-matrix into a statement/mutant suspiciousness vector. Usage:

    crush-matrix \
      --formula (tarantula|ochiai|dstar2|barinel|opt2|muse|jaccard) \
      --matrix FILE \
      --element-type (Statement|Mutant) \
      --element-names FILE \
      --total-defn (tests|mutants) \
      [--hybrid-scheme (numerator|constant|mirror|coverage-only) \
       --hybrid-coverage-matrix FILE] \
      --output FILE

where `--element-type` indicates whether the entries of the resulting vector correspond to statements or mutants;

and `--element-names` is the path to a file whose nth line identifies the code element (statement/mutant) to which the nth matrix column refers

and `--total-defn` indicates whether, in the formula, "totalpassed" should refer to the number of passing tests, or the number of times a passing test covers/kills an element. (And the same for "totalfailed".)

`--hybrid-scheme` and `--hybrid-coverage-matrix` should come together or not at all. They should be present iff the FLT being performed belonged to the "hybrid" family; in this case,

    * `--matrix` indicates the *mutant kill-matrix* (telling which tests kill which mutants),
    * `--hybrid-coverage-matrix` indicates the *mutant coverage-matrix* (telling which tests cover which mutants), and
    * `--hybrid-scheme` indicates how the two matrices are combined: if `numerator`, mutants covered by failing tests will have some small/moderate increase in suspiciousness (usually by incrementing the numerator of some fraction by 1); if `constant`, mutants covered by failing tests will have some large increase in suspiciousness (incrementing the whole suspiciousness by 1); if `mirror`, each mutant's suspiciousness will be the sum of (the formula applied to its column in the kill-matrix) and (the formula applied to its column in the coverage-matrix); if  `coverage-only`, the formula will *only* be applied to its column in the coverage-matrix, and the kill-matrix will be ignored.

"""

from __future__ import division
import collections
import re
import sys
import traceback

#from formulas import *

############################################################################################################
#!/usr/bin/python

import math

def sqrt(value):
  return value**0.5

def tarantula(passed, failed, totalpassed, totalfailed):
  if totalfailed == 0 or failed == 0:
    return 0
  if totalpassed == 0:
    assert passed == 0
    return 1 if failed > 0 else 0
  return (failed/totalfailed)/(failed/totalfailed + passed/totalpassed)
def tarantula_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if totalfailed == 0 or failed == 0:
    return 0
  if totalpassed == 0:
    assert passed == 0
    return 1 if failed > 0 else 0
  return (passed/totalpassed + (1 if was_covered else 0)/(passed/totalpassed + failed/totalfailed))

def ochiai(passed, failed, totalpassed, totalfailed):
  if totalfailed == 0 or (passed+failed == 0):
    return 0
  return failed/(totalfailed*(failed+passed))**0.5
def ochiai_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if totalfailed == 0 or (passed+failed == 0):
    return 0
  return (failed + (1 if was_covered else 0))/(totalfailed*(failed+passed))**0.5

def ochiai2(passed, failed, totalpassed, totalfailed):
  return (failed * (totalpassed - passed)) / sqrt((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) * (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)))
def ochiai2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed * (totalpassed - passed) + (1 if was_covered else 0)) / sqrt((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) * (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)))

def opt1(passed, failed, totalpassed, totalfailed):
  if (totalfailed - failed) > 0:
    return -1
  return (totalpassed - passed)
def opt1_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if (totalfailed - failed) > 0:
    return -1
  return (totalpassed - passed) + (1 if was_covered else 0)

def opt2(passed, failed, totalpassed, totalfailed):
  return failed - passed/(totalpassed+1)
def opt2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return failed - (passed-(1 if was_covered else 0))/(totalpassed+1)

def barinel(passed, failed, totalpassed, totalfailed):
  if failed == 0:
    return 0
  h = passed/(passed+failed)
  return 1-h
def barinel_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if failed == 0:
    return 0
  h = (passed - (1 if was_covered else 0))/(passed+failed)
  return 1-h

def dstar2(passed, failed, totalpassed, totalfailed):
  if passed + totalfailed - failed == 0:
    assert passed==0 and failed==totalfailed
    return totalfailed**2 + 1 # slightly higher than otherwise possible
  return failed**2 / (passed + totalfailed - failed)
def dstar2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if passed + totalfailed - failed == 0:
    assert passed==0 and failed==totalfailed
    return totalfailed**2 + 2 # slightly higher than otherwise possible
  return (failed**2 + (1 if was_covered else 0)) / (passed + totalfailed - failed)

def muse(passed, failed, totalpassed, totalfailed):
  if totalpassed == 0:
    return 0
  return failed - totalfailed/totalpassed * passed
def muse_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if totalpassed == 0:
    return 0
  return failed - (totalfailed-(1 if was_covered else 0))/totalpassed * passed

def jaccard(passed, failed, totalpassed, totalfailed):
  if totalfailed + passed == 0:
    return failed
  return failed / (totalfailed + passed)
def jaccard_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if totalfailed + passed == 0:
    return (failed + (1 if was_covered else 0))
  return (failed + (1 if was_covered else 0)) / (totalfailed + passed)

def gp02(passed, failed, totalpassed, totalfailed):
  return 2 * (failed + sqrt(totalpassed - passed)) + sqrt(passed)
def gp02_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return gp02(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def gp03(passed, failed, totalpassed, totalfailed):
  return sqrt(abs(pow(failed, 2) - sqrt(passed)))
def gp03_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return gp03(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def gp13(passed, failed, totalpassed, totalfailed):
  return failed * (1 + (1 / (2 * passed + failed)))
def gp13_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return gp13(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def gp19(passed, failed, totalpassed, totalfailed):
  return failed * sqrt(abs(passed - failed + (totalfailed - failed) - (totalpassed - passed)))
def gp19_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return gp19(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def anderberg(passed, failed, totalpassed, totalfailed):
  return failed / (failed + 2 * ((totalfailed - failed) + passed))
def anderberg_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / (failed + 2 * ((totalfailed - failed) + passed))

def dice(passed, failed, totalpassed, totalfailed):
  return (2 * failed) / (failed + (totalfailed - failed) + passed)
def dice_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 * failed + (1 if was_covered else 0)) / (failed + (totalfailed - failed) + passed)

def sorensen_dice(passed, failed, totalpassed, totalfailed):
  return (2 * failed) / (2 * failed + (totalfailed - failed) + passed)
def sorensen_dice_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 * failed + (1 if was_covered else 0)) / (2 * failed + (totalfailed - failed) + passed)

def goodman(passed, failed, totalpassed, totalfailed):
  return (2 * failed - (totalfailed - failed) - passed) / (2 * failed + (totalfailed - failed) + passed)
def goodman_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 * failed - (totalfailed - failed) - passed + (1 if was_covered else 0)) / (2 * failed + (totalfailed - failed) + passed)

def qe(passed, failed, totalpassed, totalfailed):
  return failed / (failed + passed)
def qe_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / (failed + passed)

def cbi_inc(passed, failed, totalpassed, totalfailed):
  return (failed / failed + passed) - ((totalfailed - failed) / ((totalfailed - failed) + (totalpassed - passed)))
def cbi_inc_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return ((failed + (1 if was_covered else 0)) / failed + passed) - ((totalfailed - failed) / ((totalfailed - failed) + (totalpassed - passed)))

def cbi_sqrt(passed, failed, totalpassed, totalfailed):
  return 2 / ((1 / cbi_inc(passed, failed, totalpassed, totalfailed)) + (sqrt(totalfailed - failed) / sqrt(failed)))
def cbi_sqrt_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 + (1 if was_covered else 0)) / ((1 / cbi_inc(passed, failed, totalpassed, totalfailed)) + (sqrt(totalfailed - failed) / sqrt(failed)))

def cbi_log(passed, failed, totalpassed, totalfailed):
  if failed == 0 or totalfailed - failed == 0:
    return 0
  return 2 / ((1 / cbi_inc(passed, failed, totalpassed, totalfailed)) + (math.log(totalfailed - failed) / math.log(failed)))
def cbi_log_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  if failed == 0 or totalfailed - failed == 0:
    return 0
  return (2 + (1 if was_covered else 0)) / ((1 / cbi_inc(passed, failed, totalpassed, totalfailed)) + (math.log(totalfailed - failed) / math.log(failed)))

def wong1(passed, failed, totalpassed, totalfailed):
  return failed
def wong1_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return wong1(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def wong2(passed, failed, totalpassed, totalfailed):
  return failed - passed
def wong2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return wong2(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def wong3(passed, failed, totalpassed, totalfailed):
  if passed <= 2:
    return passed
  if passed > 2 and passed <= 10:
    h = 2 + 0.1 * (passed - 2)
  else: # passed > 10
    h = 2.8 + 0.001 * (passed - 10)
  return failed - h
def wong3_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return wong3(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def hamann(passed, failed, totalpassed, totalfailed):
  return (failed + (totalpassed - passed) - (totalfailed - failed) - passed) / (failed + (totalfailed - failed) + passed + (totalpassed - passed))
def hamann_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (totalpassed - passed) - (totalfailed - failed) - passed + (1 if was_covered else 0)) / (failed + (totalfailed - failed) + passed + (totalpassed - passed))

def simple_matching(passed, failed, totalpassed, totalfailed):
  return (failed + (totalpassed - passed)) / (failed + passed + (totalpassed - passed) + (totalfailed - failed))
def simple_matching_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (totalpassed - passed) + (1 if was_covered else 0)) / (failed + passed + (totalpassed - passed) + (totalfailed - failed))

def sokal(passed, failed, totalpassed, totalfailed):
  return (2 * (failed + (totalpassed - passed))) / (2 * (failed + (totalpassed - passed)) + (totalfailed - failed) + passed)
def sokal_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 * (failed + (totalpassed - passed)) + (1 if was_covered else 0)) / (2 * (failed + (totalpassed - passed)) + (totalfailed - failed) + passed)

def rogers_tanimoto(passed, failed, totalpassed, totalfailed):
  return (failed + (totalpassed - passed)) / (failed + (totalpassed - passed) + 2 * ((totalfailed - failed) + passed))
def rogers_tanimoto_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (totalpassed - passed) + (1 if was_covered else 0)) / (failed + (totalpassed - passed) + 2 * ((totalfailed - failed) + passed))

def hamming(passed, failed, totalpassed, totalfailed):
  return failed + (totalpassed - passed)
def hamming_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return hamming(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def euclid(passed, failed, totalpassed, totalfailed):
  return sqrt(failed + (totalpassed - passed))
def euclid_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return euclid(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def russell_rao(passed, failed, totalpassed, totalfailed):
  return failed / (failed + (totalfailed - failed) + passed + (totalpassed - passed))
def russell_rao_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / (failed + (totalfailed - failed) + passed + (totalpassed - passed))

def binary(passed, failed, totalpassed, totalfailed):
  if failed < totalfailed:
    return 0
  return 1 # failed == totalfailed
def binary_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return binary(passed, failed, totalpassed, totalfailed) + (1 if was_covered else 0)

def scott(passed, failed, totalpassed, totalfailed):
  return (4 * (failed * (totalpassed - passed)) - 4 * ((totalfailed - failed) * passed) - pow((totalfailed - failed) - passed, 2)) / ((2 * failed + (totalfailed - failed) + passed) * (2 * (totalpassed - passed) + (totalfailed - failed) + passed))
def scott_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (4 * (failed * (totalpassed - passed)) - 4 * ((totalfailed - failed) * passed) - pow((totalfailed - failed) - passed, 2) + (1 if was_covered else 0)) / ((2 * failed + (totalfailed - failed) + passed) * (2 * (totalpassed - passed) + (totalfailed - failed) + passed))

def rogot1(passed, failed, totalpassed, totalfailed):
  a = failed / (2 * failed + (totalfailed - failed) + passed)
  b = (totalpassed - passed) / (2 * (totalpassed - passed) + (totalfailed - failed) + passed)
  return 0.5 * (a + b)
def rogot1_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  a = (failed + (1 if was_covered else 0)) / (2 * failed + (totalfailed - failed) + passed)
  b = (totalpassed - passed) / (2 * (totalpassed - passed) + (totalfailed - failed) + passed)
  return 0.5 * (a + b)

def rogot2(passed, failed, totalpassed, totalfailed):
  a = failed / (failed + passed)
  b = failed / (totalfailed - failed)
  c = (totalpassed - passed) / ((totalpassed - passed) + passed)
  d = (totalpassed - passed) / ((totalpassed - passed) + (totalfailed - failed))
  return 0.25 * (a + b + c + d)
def rogot2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  a = (failed + (1 if was_covered else 0)) / (failed + passed)
  b = failed / (totalfailed - failed)
  c = (totalpassed - passed) / ((totalpassed - passed) + passed)
  d = (totalpassed - passed) / ((totalpassed - passed) + (totalfailed - failed))
  return 0.25 * (a + b + c + d)

def kulczynski1(passed, failed, totalpassed, totalfailed):
  return failed / ((totalfailed - failed) + passed)
def kulczynski1_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / ((totalfailed - failed) + passed)

def kulczynski2(passed, failed, totalpassed, totalfailed):
  a = failed / (failed + (totalfailed - failed))
  b = failed / (failed + passed)
  return 0.5 * (a + b)
def kulczynski2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  a = (failed + (1 if was_covered else 0)) / (failed + (totalfailed - failed))
  b = failed / (failed + passed)
  return 0.5 * (a + b)

def m1(passed, failed, totalpassed, totalfailed):
  return (failed + (totalpassed - passed)) / ((totalfailed - failed) + passed)
def m1_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (totalpassed - passed) + (1 if was_covered else 0)) / ((totalfailed - failed) + passed)

def m2(passed, failed, totalpassed, totalfailed):
  return failed / (failed + (totalpassed - passed) + 2 * ((totalfailed - failed) + passed))
def m2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / (failed + (totalpassed - passed) + 2 * ((totalfailed - failed) + passed))

def ample(passed, failed, totalpassed, totalfailed):
  return abs(ample2(passed, failed, totalpassed, totalfailed))
def ample_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return abs(ample2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered))

def ample2(passed, failed, totalpassed, totalfailed):
  return (failed / (totalfailed - failed)) - (passed / (totalpassed - passed))
def ample2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return ((failed + (1 if was_covered else 0)) / (totalfailed - failed)) - (passed / (totalpassed - passed))

def arithmetic_mean(passed, failed, totalpassed, totalfailed):
  return (2 * failed * (totalpassed - passed) - 2 * (totalfailed - failed) * passed) / ((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) + (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)))
def arithmetic_mean_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 * failed * (totalpassed - passed) - 2 * (totalfailed - failed) * passed + (1 if was_covered else 0)) / ((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) + (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)))

def geometric_mean(passed, failed, totalpassed, totalfailed):
  return (failed * (totalpassed - passed) - (totalfailed - failed) * passed) / sqrt((failed + passed) * (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)) * ((totalfailed - failed) + (totalpassed - passed)))
def geometric_mean_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed * (totalpassed - passed) - (totalfailed - failed) * passed + (1 if was_covered else 0)) / sqrt((failed + passed) * (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)) * ((totalfailed - failed) + (totalpassed - passed)))

def harmonic_mean(passed, failed, totalpassed, totalfailed):
  return (failed * (totalpassed - passed) - (totalfailed - failed) * passed) * ((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) + (failed + (totalfailed - failed)) * (passed + (totalpassed - passed))) / ((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) * (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)))
def harmonic_mean_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return ((failed * (totalpassed - passed) - (totalfailed - failed) * passed) * ((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) + (failed + (totalfailed - failed)) * (passed + (totalpassed - passed))) + (1 if was_covered else 0)) / ((failed + passed) * ((totalpassed - passed) + (totalfailed - failed)) * (failed + (totalfailed - failed)) * (passed + (totalpassed - passed)))

def cohen(passed, failed, totalpassed, totalfailed):
  return (2 * (failed * (totalpassed - passed) - (totalfailed - failed) * passed)) / ((failed + passed) * ((totalpassed - passed) + passed) + (failed + (totalfailed - failed)) * ((totalfailed - failed) + (totalpassed - passed)))
def cohen_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (2 * (failed * (totalpassed - passed) - (totalfailed - failed) * passed) + (1 if was_covered else 0)) / ((failed + passed) * ((totalpassed - passed) + passed) + (failed + (totalfailed - failed)) * ((totalfailed - failed) + (totalpassed - passed)))

def fleiss(passed, failed, totalpassed, totalfailed):
  return (4 * (failed * (totalpassed - passed) - (totalfailed - failed) * passed) - pow((totalfailed - failed) - passed, 2)) / ((2 * failed + (totalfailed - failed) + passed) + (2 * (totalpassed - passed) + (totalfailed - failed) + passed))
def fleiss_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (4 * (failed * (totalpassed - passed) - (totalfailed - failed) * passed) - pow((totalfailed - failed) - passed, 2) + (1 if was_covered else 0)) / ((2 * failed + (totalfailed - failed) + passed) + (2 * (totalpassed - passed) + (totalfailed - failed) + passed))

def braun_banquet(passed, failed, totalpassed, totalfailed):
  return failed / max(failed + passed, failed + (totalfailed - failed))
def braun_banquet_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / max(failed + passed, failed + (totalfailed - failed))

# TODO require sloc
# def dennis(passed, failed, totalpassed, totalfailed):
#   return ((failed * (totalpassed - passed)) - (passed * (totalfailed - failed))) / (sqrt(sloc * (failed + passed) * (failed + (totalfailed - failed))))

def mountford(passed, failed, totalpassed, totalfailed):
  return failed / (0.5 * ((failed * passed) + (failed * (totalfailed - failed))) + (passed * (totalfailed - failed)))
def mountford_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / (0.5 * ((failed * passed) + (failed * (totalfailed - failed))) + (passed * (totalfailed - failed)))

# TODO require sloc
# def fossum(passed, failed, totalpassed, totalfailed):
#   return (sloc * pow(failed - 0.5, 2)) / ((failed + passed) + (failed + (totalfailed - failed)))

# TODO require sloc
# def pearson(passed, failed, totalpassed, totalfailed):
#   return sloc * pow((failed * (totalpassed - passed)) - (passed * (totalfailed - failed)), 2) / ((passed + failed) * ((totalpassed - passed) + (totalfailed - failed)) * totalpassed * totalfailed)

def gower(passed, failed, totalpassed, totalfailed):
  return (failed + (totalpassed - passed)) / sqrt(totalfailed * (passed + failed) * ((totalpassed - passed) + (totalfailed - failed)) * totalpassed)
def gower_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (totalpassed - passed) + (1 if was_covered else 0)) / sqrt(totalfailed * (passed + failed) * ((totalpassed - passed) + (totalfailed - failed)) * totalpassed)

def michael(passed, failed, totalpassed, totalfailed):
  return (4 * ((failed * (totalpassed - passed)) - (passed * (totalfailed - failed)))) / (pow(failed + (totalpassed - passed), 2) + pow(passed + (totalfailed - failed), 2))
def michael_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (4 * ((failed * (totalpassed - passed)) - (passed * (totalfailed - failed))) + (1 if was_covered else 0)) / (pow(failed + (totalpassed - passed), 2) + pow(passed + (totalfailed - failed), 2))

def pierce(passed, failed, totalpassed, totalfailed):
  return ((failed * (totalfailed - failed)) + ((totalfailed - failed) * passed)) / ((failed * (totalfailed - failed)) + (2 * ((totalfailed - failed) * (totalpassed - passed))) + (passed * (totalpassed - passed)))
def pierce_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return ((failed * (totalfailed - failed)) + ((totalfailed - failed) * passed) + (1 if was_covered else 0)) / ((failed * (totalfailed - failed)) + (2 * ((totalfailed - failed) * (totalpassed - passed))) + (passed * (totalpassed - passed)))

def baroni_urbani_buser(passed, failed, totalpassed, totalfailed):
  return (sqrt(failed * (totalpassed - passed)) + failed) / (sqrt(failed * (totalpassed - passed)) + failed + passed + (totalfailed - failed))
def baroni_urbani_buser_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (sqrt(failed * (totalpassed - passed)) + failed + (1 if was_covered else 0)) / (sqrt(failed * (totalpassed - passed)) + failed + passed + (totalfailed - failed))

# TODO require sloc
# def tarwid(passed, failed, totalpassed, totalfailed):
#   return ((sloc * failed) - (totalfailed * (passed + failed))) / ((n * failed) + (totalfailed * (passed + failed)))

def zoltar(passed, failed, totalpassed, totalfailed):
  return failed / (failed + (totalfailed - failed) + passed + ((1000 * (totalfailed - failed) * passed) / failed))
def zoltar_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / (failed + (totalfailed - failed) + passed + ((1000 * (totalfailed - failed) * passed) / failed))

def overlap(passed, failed, totalpassed, totalfailed):
  return failed / min(failed, (totalfailed - failed), passed)
def overlap_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
  return (failed + (1 if was_covered else 0)) / min(failed, (totalfailed - failed), passed)

FORMULAS = {
  'tarantula': tarantula,
  'ochiai': ochiai,
  'ochiai2': ochiai2,
  'opt1': opt1,
  'opt2': opt2,
  'barinel': barinel,
  'dstar2': dstar2,
  'muse': muse,
  'jaccard': jaccard,
  'gp02': gp02,
  'gp03': gp03,
  'gp13': gp13,
  'gp19': gp19,
  'anderberg': anderberg,
  'dice': dice,
  'sorensen_dice': sorensen_dice,
  'goodman': goodman,
  'qe': qe,
  'cbi_inc': cbi_inc,
  'cbi_sqrt': cbi_sqrt,
  'cbi_log': cbi_log,
  'wong1': wong1,
  'wong2': wong2,
  'wong3': wong3,
  'hamann': hamann,
  'simple_matching': simple_matching,
  'sokal': sokal,
  'rogers_tanimoto': rogers_tanimoto,
  'hamming': hamming,
  'euclid': euclid,
  'russell_rao': russell_rao,
  'binary': binary,
  'scott': scott,
  'rogot1': rogot1,
  'rogot2': rogot2,
  'kulczynski1': kulczynski1,
  'kulczynski2': kulczynski2,
  'm1': m1,
  'm2': m2,
  'ample': ample,
  'ample2': ample2,
  'arithmetic_mean': arithmetic_mean,
  'geometric_mean': geometric_mean,
  'harmonic_mean': harmonic_mean,
  'cohen': cohen,
  'fleiss': fleiss,
  'braun_banquet': braun_banquet,
  # 'dennis': dennis,
  'mountford': mountford,
  # 'fossum': fossum,
  # 'pearson': pearson,
  'gower': gower,
  'michael': michael,
  'pierce': pierce,
  'baroni_urbani_buser': baroni_urbani_buser,
  # 'tarwid': tarwid,
  'zoltar': zoltar,
  'overlap': overlap
}

HYBRID_NUMERATOR_FORMULAS = {
  'tarantula': tarantula_hybrid_numerator,
  'ochiai': ochiai_hybrid_numerator,
  'ochiai2': ochiai2_hybrid_numerator,
  'opt1': opt1_hybrid_numerator,
  'opt2': opt2_hybrid_numerator,
  'barinel': barinel_hybrid_numerator,
  'dstar2': dstar2_hybrid_numerator,
  'muse': muse_hybrid_numerator,
  'jaccard': jaccard_hybrid_numerator,
  'gp02': gp02_hybrid_numerator,
  'gp03': gp03_hybrid_numerator,
  'gp13': gp13_hybrid_numerator,
  'gp19': gp19_hybrid_numerator,
  'anderberg': anderberg_hybrid_numerator,
  'dice': dice_hybrid_numerator,
  'sorensen_dice': sorensen_dice_hybrid_numerator,
  'goodman': goodman_hybrid_numerator,
  'qe': qe_hybrid_numerator,
  'cbi_inc': cbi_inc_hybrid_numerator,
  'cbi_sqrt': cbi_sqrt_hybrid_numerator,
  'cbi_log': cbi_log_hybrid_numerator,
  'wong1': wong1_hybrid_numerator,
  'wong2': wong2_hybrid_numerator,
  'wong3': wong3_hybrid_numerator,
  'hamann': hamann_hybrid_numerator,
  'simple_matching': simple_matching_hybrid_numerator,
  'sokal': sokal_hybrid_numerator,
  'rogers_tanimoto': rogers_tanimoto_hybrid_numerator,
  'hamming': hamming_hybrid_numerator,
  'euclid': euclid_hybrid_numerator,
  'russell_rao': russell_rao_hybrid_numerator,
  'binary': binary_hybrid_numerator,
  'scott': scott_hybrid_numerator,
  'rogot1': rogot1_hybrid_numerator,
  'rogot2': rogot2_hybrid_numerator,
  'kulczynski1': kulczynski1_hybrid_numerator,
  'kulczynski2': kulczynski2_hybrid_numerator,
  'm1': m1_hybrid_numerator,
  'm2': m2_hybrid_numerator,
  'ample': ample_hybrid_numerator,
  'ample2': ample2_hybrid_numerator,
  'arithmetic_mean': arithmetic_mean_hybrid_numerator,
  'geometric_mean': geometric_mean_hybrid_numerator,
  'harmonic_mean': harmonic_mean_hybrid_numerator,
  'cohen': cohen_hybrid_numerator,
  'fleiss': fleiss_hybrid_numerator,
  'braun_banquet': braun_banquet_hybrid_numerator,
  # 'dennis': dennis_hybrid_numerator,
  'mountford': mountford_hybrid_numerator,
  # 'fossum': fossum_hybrid_numerator,
  # 'pearson': pearson_hybrid_numerator,
  'gower': gower_hybrid_numerator,
  'michael': michael_hybrid_numerator,
  'pierce': pierce_hybrid_numerator,
  'baroni_urbani_buser': baroni_urbani_buser_hybrid_numerator,
  # 'tarwid': tarwid_hybrid_numerator,
  'zoltar': zoltar_hybrid_numerator,
  'overlap': overlap_hybrid_numerator
}

############################################################################################################

def crush_row(formula, hybrid_scheme, passed, failed, totalpassed, totalfailed, passed_covered=None, failed_covered=None, totalpassed_covered=0.0, totalfailed_covered=0.0):
  '''Returns the suspiciousness of a statement or mutant.

  ``formula`` (a string) is the name of the formula to plug passed/failed/totalpassed/totalfailed into.

  ``hybrid_scheme`` ("numerator", "constant", or "mirror"), useful for MBFL only, specifies how the formula should be modified to incorporate the number of passing/failing tests that *cover* the mutant (rather than kill it).
  '''
  try:
    if hybrid_scheme is None:
      return FORMULAS[formula](passed, failed, totalpassed, totalfailed)
    elif hybrid_scheme == 'numerator':
      return HYBRID_NUMERATOR_FORMULAS[formula](passed, failed, totalpassed, totalfailed, failed_covered > 0)
    elif hybrid_scheme == 'constant':
      return FORMULAS[formula](passed, failed, totalpassed, totalfailed) + (1 if failed_covered > 0 else 0)
    elif hybrid_scheme == 'mirror':
      return (FORMULAS[formula](passed, failed, totalpassed, totalfailed) +
              FORMULAS[formula](passed_covered, failed_covered, totalpassed_covered, totalfailed_covered))/2.
    elif hybrid_scheme == 'coverage-only':
      return FORMULAS[formula](passed_covered, failed_covered, totalpassed_covered, totalfailed_covered)
    raise ValueError('unrecognized hybrid scheme name: {!r}'.format(hybrid_scheme))
  except ZeroDivisionError as zeroDivisionError:
    sys.stderr.write("Warn: catch integer division or modulo by zero for " + formula + "\n")
    sys.stderr.write("Passed: " + str(passed) + "\nFailed: " + str(failed) + "\nTotalPassed: " + str(totalpassed) + "\nTotalFailed: " + str(totalfailed) + "\n")
    return 0
  except:
    traceback.print_exc()
    sys.stderr.write("Passed: " + str(passed) + "\nFailed: " + str(failed) + "\nTotalPassed: " + str(totalpassed) + "\nTotalFailed: " + str(totalfailed) + "\n")
    sys.exit(1)

def suspiciousnesses_from_tallies(formula, hybrid_scheme, tally, hybrid_coverage_tally):
  '''Returns a dict mapping element-number to suspiciousness.
  '''
  if hybrid_coverage_tally is None:
    passed_covered = failed_covered = collections.defaultdict(lambda: None)
    totalpassed_covered = totalfailed_covered = 0
  else:
    passed_covered = hybrid_coverage_tally.passed
    failed_covered = hybrid_coverage_tally.failed
    totalpassed_covered = hybrid_coverage_tally.totalpassed
    totalfailed_covered = hybrid_coverage_tally.totalfailed

  return {
    element: crush_row(
      formula=formula, hybrid_scheme=hybrid_scheme,
      passed=float(tally.passed[element]), failed=float(tally.failed[element]),
      totalpassed=float(tally.totalpassed), totalfailed=float(tally.totalfailed),
      passed_covered=passed_covered[element], failed_covered=failed_covered[element],
      totalpassed_covered=float(totalpassed_covered), totalfailed_covered=float(totalfailed_covered))
    for element in range(tally.n_elements)}


TestSummary = collections.namedtuple('TestSummary', ('triggering', 'covered_elements'))
def parse_test_summary(line, n_elements):
  words = line.strip().split(' ')
  coverages, sign = words[:-1], words[-1]
  if len(coverages) != n_elements:
    raise ValueError("expected {expected} elements in each row, got {actual} in {line!r}".format(expected=n_elements, actual=len(coverages), line=line))
  return TestSummary(
    triggering=(sign == '-'),
    covered_elements=set(i for i in range(len(words)) if words[i]=='1'))

PassFailTally = collections.namedtuple('PassFailTally', ('n_elements', 'passed', 'failed', 'totalpassed', 'totalfailed'))
def tally_matrix(matrix_file, total_defn, n_elements):
  '''Returns a PassFailTally describing how many passing/failing tests there are, and how many of each cover each code element.

  ``total_defn`` may be "tests" (in which case the tally's ``totalpassed`` will be the number of passing tests) or "elements" (in which case it'll be the number of times a passing test covers a code element) (and same for ``totalfailed``).

  ``n_elements`` is the number of code elements that each row of the matrix should indicate coverage for.
  '''
  summaries = (parse_test_summary(line, n_elements) for line in matrix_file)

  passed = {i: 0 for i in range(n_elements)}
  failed = {i: 0 for i in range(n_elements)}
  totalpassed = 0
  totalfailed = 0
  for summary in summaries:
    if summary.triggering:
      totalfailed += (1 if total_defn == 'tests' else len(summary.covered_elements))
      for element_number in summary.covered_elements:
        failed[element_number] += 1
    else:
      totalpassed += (1 if total_defn == 'tests' else len(summary.covered_elements))
      for element_number in summary.covered_elements:
        passed[element_number] += 1

  return PassFailTally(n_elements, passed, failed, totalpassed, totalfailed)

if __name__ == '__main__':

  import argparse
  import csv

  parser = argparse.ArgumentParser()
  parser.add_argument('--formula', required=True, choices=set(FORMULAS.keys()))
  parser.add_argument('--matrix', required=True, help='path to the coverage/kill-matrix')
  parser.add_argument('--hybrid-scheme', choices=['numerator', 'constant', 'mirror', 'coverage-only'])
  parser.add_argument('--hybrid-coverage-matrix', help='optional coverage matrix for hybrid techniques')
  parser.add_argument('--element-type', required=True, choices=['Statement', 'Mutant'], help='file enumerating names for matrix columns')
  parser.add_argument('--element-names', required=True, help='file enumerating names for matrix columns')
  parser.add_argument('--total-defn', required=True, choices=['tests', 'elements'], help='whether totalpassed/totalfailed should counts tests or covered/killed elements')
  parser.add_argument('--output', required=True, help='file to write suspiciousness vector to')

  args = parser.parse_args()

  if (args.hybrid_scheme is None) != (args.hybrid_coverage_matrix is None):
    raise RuntimeError('--hybrid-scheme and --hybrid-coverage-matrix should come together or not at all')

  with open(args.element_names) as name_file:
    element_names = {i: name.strip() for i, name in enumerate(name_file)}

  n_elements = len(element_names)

  with open(args.matrix) as matrix_file:
    tally = tally_matrix(matrix_file, args.total_defn, n_elements=n_elements)

  if args.hybrid_scheme is None:
    hybrid_coverage_tally = None
  else:
    with open(args.hybrid_coverage_matrix) as coverage_matrix_file:
      hybrid_coverage_tally = tally_matrix(coverage_matrix_file, args.total_defn, n_elements)


  suspiciousnesses = suspiciousnesses_from_tallies(
    formula=args.formula, hybrid_scheme=args.hybrid_scheme,
    tally=tally, hybrid_coverage_tally=hybrid_coverage_tally)

  with open(args.output, 'w') as output_file:
    writer = csv.DictWriter(output_file, [args.element_type,'Suspiciousness'])
    writer.writeheader()
    for element in range(n_elements):
      writer.writerow({
        args.element_type: element_names[element],
        'Suspiciousness': suspiciousnesses[element]})
