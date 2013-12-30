import unittest
import numpy as np

from Orange import data
from Orange.evaluation.testing import CrossValidation, LeaveOneOut
from Orange.classification import naive_bayes, majority


class TestingTestCase(unittest.TestCase):
    def test_no_data(self):
        self.assertRaises(AttributeError, CrossValidation,
                          fitters=[naive_bayes.BayesLearner()])


class CrossValidationTestCase(unittest.TestCase):
    @staticmethod
    def random_data(nrows, ncols):
        x = np.random.random_integers(1, 3, (nrows, ncols))
        col = np.random.randint(ncols)
        y = x[:nrows, col].reshape(nrows, 1)
        return data.Table(x, y)

    def test_results(self):
        nrows, ncols = 1000, 10
        t = self.random_data(nrows, ncols)
        res = CrossValidation(t, [naive_bayes.BayesLearner()])
        y = t.Y
        np.testing.assert_equal(res.actual, y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(res.predicted[0],
                                y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(np.argmax(res.probabilities[0], axis=1),
                                y[res.row_indices].reshape(nrows))
        self.assertEqual(len(res.folds), 10)
        for i, fold in enumerate(res.folds):
            self.assertEquals(fold.start, i * 100)
            self.assertEquals(fold.stop, (i + 1) * 100)

    def test_folds(self):
        nrows, ncols = 1000, 10
        t = self.random_data(nrows, ncols)
        res = CrossValidation(t, [naive_bayes.BayesLearner()], k=5)
        self.assertEqual(len(res.folds), 5)
        for i, fold in enumerate(res.folds):
            self.assertEquals(fold.start, i * 200)
            self.assertEquals(fold.stop, (i + 1) * 200)

    def test_call_5(self):
        cv = CrossValidation(k=5)
        nrows, ncols = 1000, 10
        t = self.random_data(nrows, ncols)
        res = cv(t, [naive_bayes.BayesLearner()])
        y = t.Y
        np.testing.assert_equal(res.actual, y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(res.predicted[0],
                                y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(np.argmax(res.probabilities[0], axis=1),
                                y[res.row_indices].reshape(nrows))
        self.assertEqual(len(res.folds), 5)
        for i, fold in enumerate(res.folds):
            self.assertEquals(fold.start, i * 200)
            self.assertEquals(fold.stop, (i + 1) * 200)

    def test_store_data(self):
        nrows, ncols = 1000, 10
        t = self.random_data(nrows, ncols)
        fitters = [naive_bayes.BayesLearner()]

        cv = CrossValidation()
        res = cv(t, fitters)
        self.assertIsNone(res.data)

        cv = CrossValidation(store_data=True)
        res = cv(t, fitters)
        self.assertIs(res.data, t)

        res = CrossValidation(t, fitters)
        self.assertIsNone(res.data)

        res = CrossValidation(t, fitters, store_data=True)
        self.assertIs(res.data, t)

    def test_store_models(self):
        nrows, ncols = 1000, 10
        t = self.random_data(nrows, ncols)
        fitters = [naive_bayes.BayesLearner(), majority.MajorityFitter()]

        cv = CrossValidation(k=5)
        res = cv(t, fitters)
        self.assertIsNone(res.models)

        cv = CrossValidation(k=5, store_models=True)
        res = cv(t, fitters)
        self.assertEquals(len(res.models), 5)
        for models in res.models:
            self.assertEquals(len(models), 2)
            self.assertIsInstance(models[0], naive_bayes.BayesClassifier)
            self.assertIsInstance(models[1], majority.ConstantClassifier)

        cv = CrossValidation(k=5)
        res = cv(t, fitters)
        self.assertIsNone(res.models)

        res = CrossValidation(t, fitters, k=5, store_models=True)
        self.assertEquals(len(res.models), 5)
        for models in res.models:
            self.assertEquals(len(models), 2)
            self.assertIsInstance(models[0], naive_bayes.BayesClassifier)
            self.assertIsInstance(models[1], majority.ConstantClassifier)

    def test_10_fold_probs(self):
        self.data = data.Table('iris')[30:130]
        self.fitters = [majority.MajorityFitter(), majority.MajorityFitter()]

        results = CrossValidation(k=10)(self.data, self.fitters)

        self.assertEqual(results.predicted.shape, (2, len(self.data)))
        np.testing.assert_equal(results.predicted, np.ones((2, 100)))
        probs = results.probabilities
        self.assertTrue((probs[:, :, 0] < probs[:, :, 2]).all())
        self.assertTrue((probs[:, :, 2] < probs[:, :, 1]).all())



class LeaveOneOutTestCase(unittest.TestCase):
    @staticmethod
    def random_data(nrows, ncols):
        x = np.random.random_integers(1, 3, (nrows, ncols))
        col = np.random.randint(ncols)
        y = x[:nrows, col].reshape(nrows, 1)
        return data.Table(x, y)

    def test_results(self):
        nrows, ncols = 50, 10
        t = self.random_data(nrows, ncols)
        res = LeaveOneOut(t, [naive_bayes.BayesLearner()])
        y = t.Y
        np.testing.assert_equal(res.actual, y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(res.predicted[0],
                                y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(np.argmax(res.probabilities[0], axis=1),
                                y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(res.row_indices, np.arange(nrows))

    def test_call(self):
        cv = LeaveOneOut()
        nrows, ncols = 50, 10
        t = self.random_data(nrows, ncols)
        res = cv(t, [naive_bayes.BayesLearner()])
        y = t.Y
        np.testing.assert_equal(res.actual, y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(res.predicted[0],
                                y[res.row_indices].reshape(nrows))
        np.testing.assert_equal(np.argmax(res.probabilities[0], axis=1),
                                y[res.row_indices].reshape(nrows))

    def test_store_data(self):
        nrows, ncols = 50, 10
        t = self.random_data(nrows, ncols)
        fitters = [naive_bayes.BayesLearner()]

        cv = LeaveOneOut()
        res = cv(t, fitters)
        self.assertIsNone(res.data)

        cv = LeaveOneOut(store_data=True)
        res = cv(t, fitters)
        self.assertIs(res.data, t)

        res = LeaveOneOut(t, fitters)
        self.assertIsNone(res.data)

        res = LeaveOneOut(t, fitters, store_data=True)
        self.assertIs(res.data, t)

    def test_store_models(self):
        nrows, ncols = 50, 10
        t = self.random_data(nrows, ncols)
        fitters = [naive_bayes.BayesLearner(), majority.MajorityFitter()]

        cv = LeaveOneOut()
        res = cv(t, fitters)
        self.assertIsNone(res.models)

        cv = LeaveOneOut(store_models=True)
        res = cv(t, fitters)
        self.assertEquals(len(res.models), 50)
        for models in res.models:
            self.assertEquals(len(models), 2)
            self.assertIsInstance(models[0], naive_bayes.BayesClassifier)
            self.assertIsInstance(models[1], majority.ConstantClassifier)

        cv = LeaveOneOut()
        res = cv(t, fitters)
        self.assertIsNone(res.models)

        res = LeaveOneOut(t, fitters, store_models=True)
        self.assertEquals(len(res.models), 50)
        for models in res.models:
            self.assertEquals(len(models), 2)
            self.assertIsInstance(models[0], naive_bayes.BayesClassifier)
            self.assertIsInstance(models[1], majority.ConstantClassifier)

    def test_probs(self):
        self.data = data.Table('iris')[30:130]
        self.fitters = [majority.MajorityFitter(), majority.MajorityFitter()]

        results = LeaveOneOut(k=10)(self.data, self.fitters)

        self.assertEqual(results.predicted.shape, (2, len(self.data)))
        np.testing.assert_equal(results.predicted, np.ones((2, 100)))
        probs = results.probabilities
        self.assertTrue((probs[:, :, 0] < probs[:, :, 2]).all())
        self.assertTrue((probs[:, :, 2] < probs[:, :, 1]).all())

