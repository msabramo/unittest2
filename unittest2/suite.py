"""TestSuite"""

import sys
import unittest
from unittest2 import case, util


class TestSuite(unittest.TestSuite):
    """A test suite is a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    in the order in which they were added, aggregating the results. When
    subclassing, do not forget to call the base class constructor.
    """
    
    def __init__(self, tests=()):
        self._tests = []
        self.addTests(tests)

    def __repr__(self):
        return "<%s tests=%s>" % (util.strclass(self.__class__), list(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return list(self) == list(other)

    def __ne__(self, other):
        return not self == other

    # Can't guarantee hash invariant, so flag as unhashable
    __hash__ = None

    def __iter__(self):
        return iter(self._tests)

    def countTestCases(self):
        cases = 0
        for test in self:
            cases += test.countTestCases()
        return cases

    def addTest(self, test):
        # sanity checks
        if not hasattr(test, '__call__'):
            raise TypeError("%r is not callable" % (test,))
        if isinstance(test, type) and issubclass(test,
                                                 (unittest.TestCase, unittest.TestSuite)):
            raise TypeError("TestCases and TestSuites must be instantiated "
                            "before passing them to addTest()")
        self._tests.append(test)

    def addTests(self, tests):
        if isinstance(tests, basestring):
            raise TypeError("tests must be an iterable of tests, not a string")
        for test in tests:
            self.addTest(test)

    def _handleClassFixture(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        self._tearDownPreviousClass(result)
        currentClass._classTornDown = False
        
        try:
            currentClass.setUpClass()
        except:
            currentClass._classSetupFailed = True
            self._addClassSetUpError(result, currentClass)
        else:
            currentClass._classSetupFailed = False
    
    def _handleModuleFixture(self, test, result):
        previousModule = None
        previousClass = getattr(result, '_previousTestClass', None)
        if previousClass is not None:
            previousModule = previousClass.__module__
        currentModule = test.__class__.__module__
        if currentModule != previousModule:
            module = sys.modules[currentModule]
            setUpModule = getattr(module, 'setUpModule', None)
            if setUpModule is not None:
                setUpModule()

    def run(self, result):
        test = None
        for test in self:
            if result.shouldStop:
                break
            
            if _isnotsuite(test):
                self._handleClassFixture(test, result)
                self._handleModuleFixture(test, result)
                result._previousTestClass = test.__class__
                
                if test.__class__._classSetupFailed:
                    continue
            
            test(result)
        
        if _isnotsuite(test):
            self._tearDownPreviousClass(result)
        return result
    
    def _tearDownPreviousClass(self, result):
        if getattr(result, '_previousTestClass', None) is None:
            return
        previousClass = result._previousTestClass
        if getattr(previousClass, '_classTornDown', True):
            return
        try:
            result._previousTestClass.tearDownClass()
        except:
            self._addClassTearDownError(result)
        previousClass._classTornDown = True

    def _addClassTearDownError(self, result):
        className = util.strclass(result._previousTestClass)
        error = _ErrorHolder('classTearDown (%s)' % className)
        result.addError(error, sys.exc_info())

    def _addClassSetUpError(self, result, klass):
        className = util.strclass(klass)
        error = _ErrorHolder('classSetUp (%s)' % className)
        result.addError(error, sys.exc_info())

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def debug(self):
        """Run the tests without collecting errors in a TestResult"""
        for test in self:
            test.debug()


class WrapperSuite(TestSuite):
    """Suites run by the TextTestRunner are wrapped with this class.
    
    It calls final class and module tearDown methods on test run end."""
    def run(self, result):
        TestSuite.run(self, result)
        self._tearDownPreviousClass(result)


class _ErrorHolder(object):
    """
    Placeholder for a TestCase inside a result. As far as a TestResult
    is concerned, this looks exactly like a unit test. Used to insert
    arbitrary errors into a test suite run.
    """
    # Inspired by the ErrorHolder from Twisted:
    # http://twistedmatrix.com/trac/browser/trunk/twisted/trial/runner.py

    # attribute used by TestResult._exc_info_to_string
    failureException = None

    def __init__(self, description):
        self.description = description

    def id(self):
        return self.description

    def shortDescription(self):
        return None

    def __repr__(self):
        return "<ErrorHolder description=%r>" % (self.description,)

    def __str__(self):
        return self.id()

    def run(self, result):
        # could call result.addError(...) - but this test-like object
        # shouldn't be run anyway
        pass

    def __call__(self, result):
        return self.run(result)

    def countTestCases(self):
        return 0

def _isnotsuite(test):
    try:
        iter(test)
    except TypeError:
        return True
    return False
