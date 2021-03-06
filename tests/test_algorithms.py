# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
import numpy
import mmap

from nidaba import algorithms
from nidaba.nidabaexceptions import (NidabaUnibarrierException,
                                     NidabaAlgorithmException)

thisfile = os.path.abspath(os.path.dirname(__file__))
resources = os.path.abspath(os.path.join(thisfile, 'resources/tesseract'))


class LevenshteinTests(unittest.TestCase):
    """Tests the edit_distance funtion by checking both the edit distance and
    full matrix comparisons."""

    # -------------------------------------------------------------------
    # Edit distance tests -----------------------------------------------
    # -------------------------------------------------------------------

    def test_equal_strings(self):
        """
        Test the edit distance of identical strings
        """
        self.assertEqual(
            0, algorithms.edit_distance('test_string', 'test_string'))

    def test_single_insert(self):
        """
        Test with strings requiring one insert
        """
        self.assertEqual(1, algorithms.edit_distance('', 'a'))

    def test_tenfold_insert(self):
        """
        Test with strings requiring ten inserts
        """
        self.assertEqual(10, algorithms.edit_distance('', 'aaaaaaaaaa'))

    def test_single_delete(self):
        """
        Test with strings requiring one delete
        """
        self.assertEqual(1, algorithms.edit_distance('a', ''))

    def test_tenfold_delete(self):
        """
        Test with strings requiring ten deletes
        """
        self.assertEqual(10, algorithms.edit_distance('aaaaaaaaaa', ''))

    def test_singledelete_singleadd(self):
        """
        Test with strings requiring a single non-trivial insert.
        """
        # Should delete the a and insert the final b.
        self.assertEqual(2, algorithms.edit_distance('abbb', 'bbbbb'))

    def test_singleadd_singledelete(self):
        """
        Test with strings requiring a single non-trivial delete.
        """

        # Should delete the a and add the final b.
        self.assertEqual(2, algorithms.edit_distance('bbbbb', 'abbb'))

    # -------------------------------------------------------------------
    # Score matrix tests ------------------------------------------------
    # -------------------------------------------------------------------

    def test_match_delete_matrix(self):
        """
        Test the scoring matrix state in an edit requiring one match and
        delete.
        """
        expected = [[0, 1, 2], [1, 0, 1]]
        self.assertEqual(expected,
                         algorithms.native_full_edit_distance('a', 'ab')[0])

    def test_match_insert_matrix(self):
        """
        Test the scoring matrix state in an edit requiring one match an insert.
        """
        expected = [[0, 1], [1, 0], [2, 1]]
        self.assertEqual(
            expected, algorithms.native_full_edit_distance('ab', 'a')[0])

    def test_all_match_matrix(self):
        """
        Test the scoring matrix state in an edit consisting only of multiple
        matches.
        """
        expected = [[0, 1, 2, 3, 4, 5],
                    [1, 0, 1, 2, 3, 4],
                    [2, 1, 0, 1, 2, 3],
                    [3, 2, 1, 0, 1, 2],
                    [4, 3, 2, 1, 0, 1],
                    [5, 4, 3, 2, 1, 0]]
        self.assertEqual(expected,
                         algorithms.native_full_edit_distance('aaaaa',
                                                              'aaaaa')[0])

    def test_all_subtitute_matrix(self):
        """
        Test the scoring matrix state in an edit consisting only of multiple
        substitutes.
        """
        expected = [[0, 1, 2, 3, 4, 5],
                    [1, 1, 2, 3, 4, 5],
                    [2, 2, 2, 3, 4, 5],
                    [3, 3, 3, 3, 4, 5],
                    [4, 4, 4, 4, 4, 5],
                    [5, 5, 5, 5, 5, 5]]
        self.assertEqual(expected,
                         algorithms.native_full_edit_distance('aaaaa',
                                                              'bbbbb')[0])

    def test_all_insert(self):
        """
        Test the scoring matrix state in an edit consisting only of multiple
        inserts.
        """
        expected = [[0, 1, 2, 3, 4, 5]]
        self.assertEqual(expected,
                         algorithms.native_full_edit_distance('', 'abcde')[0])

    def test_all_delete(self):
        """
        Test the scoring matrix state in an edit consisting only of deletes.
        """
        expected = [[0],
                    [1],
                    [2],
                    [3],
                    [4],
                    [5]]
        self.assertEqual(expected,
                         algorithms.native_full_edit_distance('abcde', '')[0])

    def test_all_empty(self):
        """
        Test the scoring matrix state in an edit between two empty strings.
        """
        expected = [[0]]
        self.assertEqual(expected,
                         algorithms.native_full_edit_distance('', '')[0])

    # -------------------------------------------------------------------
    # Parameter tests ---------------------------------------------------
    # -------------------------------------------------------------------

    def test_substitution_parameter(self):
        """
        Test the functionality of the substitution score parameter.
        """
        default = algorithms.edit_distance('a', 'b')
        same_as_default = algorithms.edit_distance(
            'a', 'b', substitutionscore=1)
        with_parameter = algorithms.edit_distance(
            'a', 'b', substitutionscore=-7)
        with_parameter_and_max = algorithms.edit_distance(
            'a', 'b', substitutionscore=7)
        self.assertEqual(1, default)
        self.assertEqual(1, same_as_default)
        self.assertEqual(-7, with_parameter)

    def test_deletion_parameter(self):
        """
        Test the functionality of the delete score parameter.
        """
        default = algorithms.edit_distance('a', '')
        same_as_default = algorithms.edit_distance('a', '', deletescore=1)
        with_parameter = algorithms.edit_distance('a', '', deletescore=-7)

        self.assertEqual(1, default)
        self.assertEqual(1, same_as_default)
        self.assertEqual(-7, with_parameter)

    def test_insertion_parameter(self):
        """
        Test the functionality of the insert score parameter.
        """
        default = algorithms.edit_distance('', 'a')
        same_as_default = algorithms.edit_distance('', 'a', insertscore=1)
        with_parameter = algorithms.edit_distance('', 'a', insertscore=-7)

        self.assertEqual(1, default)
        self.assertEqual(1, same_as_default)
        self.assertEqual(-7, with_parameter)

    def test_charmatrix_one_character_substitution_lower(self):
        """
        Test the functionality of the charmatrix parameter where in reduces the
        score of a substitution.
        """
        charmatrix = {('a', 'b'): 0}
        expected = [[0, 1],
                    [1, 0]]
        self.assertEqual(expected, algorithms.native_full_edit_distance('a',
                                                                        'b',
                                                                        charmatrix=charmatrix)[0])

    def test_charmatrix_one_character_substitution_higher(self):
        """
        Test the functionality of the charmatrix parameter where in increases
        the score of a substitution.
        """
        charmatrix = {('a', 'b'): 5}
        expected = [[0, 1],
                    [1, 5]]
        self.assertEqual(expected, algorithms.native_full_edit_distance(
            'a', 'b', charmatrix=charmatrix)[0])

    def test_charmatrix_one_character_substitution_default(self):
        """
        Test the functionality of the charmatrix parameter where it does not
        change a character score.
        """
        charmatrix = {('a', 'b'): 1}
        expected = [[0, 1],
                    [1, 1]]
        self.assertEqual(expected, algorithms.native_full_edit_distance(
            'a', 'b', charmatrix=charmatrix)[0])

    def test_charmatrix_default_delete(self):
        """
        Test the case where the charmatrix mutates the score of trivial (first
        column) deletes.
        """
        charmatrix = {('', 'a'): 5}
        expected = [[0],
                    [5],
                    [10],
                    [15]]
        self.assertEqual(expected, algorithms.native_full_edit_distance(
            'aaa', '', charmatrix=charmatrix)[0])

    def test_charmatrix_default_insert(self):
        """
        Test the case where the charmatrix mutates the score of trivial (first
        row) inserts.
        """
        charmatrix = {('a', ''): 5}
        expected = [[0, 5, 10, 15]]
        self.assertEqual(expected, algorithms.native_full_edit_distance(
            '', 'aaa', charmatrix=charmatrix)[0])
    # -------------------------------------------------------------------
    # Word tests --------------------------------------------------------
    # -------------------------------------------------------------------

    def test_identical_word(self):
        self.assertEqual(0, algorithms.edit_distance(['word'], ['word']))

    def test_word_substitution(self):
        self.assertEqual(
            1, algorithms.edit_distance(['word'], ['different word']))

    def test_word_insertion(self):
        self.assertEqual(1, algorithms.edit_distance([], ['word']))

    def test_word_deletion(self):
        self.assertEqual(1, algorithms.edit_distance(['word'], []))

    def test_word_multi_insert(self):
        self.assertEqual(5, algorithms.edit_distance([], ['word', 'word',
                                                          'word', 'word',
                                                          'word']))

    def test_word_multi_delete(self):
        self.assertEqual(5, algorithms.edit_distance(['word', 'word', 'word',
                                                      'word', 'word'], []))

    def test_word_multi_match(self):
        self.assertEqual(0, algorithms.edit_distance(['word1', 'word2',
                                                      'word3'], ['word1',
                                                                 'word2',
                                                                 'word3']))

    def test_word_multi_substitute(self):
        self.assertEqual(3, algorithms.edit_distance(['word1', 'word2',
                                                      'word3'], ['otherword1',
                                                                 'otherword2',
                                                                 'otherword3']))


class AlignmentTests(unittest.TestCase):

    def test_empty_strings(self):
        """
        Tests the edit steps between two empty strings.
        """
        self.assertEqual([], algorithms.native_align('', ''))

    def test_insertions(self):
        """
        Test the edit steps when only inserts are needed.
        """
        self.assertEqual(['i', 'i', 'i', 'i', 'i'],
                         algorithms.native_align('', 'abcde'))

    def test_deletions(self):
        """
        Test the edit steps when only deletes are needed.
        """
        self.assertEqual(['d', 'd', 'd', 'd', 'd'],
                         algorithms.native_align('abcde', ''))

    def test_matches(self):
        """
        Test the edit steps when only matches are needed.
        """
        self.assertEqual(['m', 'm', 'm', 'm', 'm'],
                         algorithms.native_align('abcde', 'abcde'))

    def test_matches_1(self):  # TODO
        """
        Test the edit steps when only substitutions are needed.
        """
        self.assertEqual(['s', 's', 's', 's', 's'],
                         algorithms.native_align('abcde', 'vwxyz'))

    def test_wikipedia_example_1(self):
        """
        Test against the first general example provided at
        http://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm
        """
        self.assertEqual(['s', 'm', 'm', 'm', 's', 'm', 'd'],
                         algorithms.native_align('sitting', 'kitten'))

    def test_wikipedia_example_2(self):
        """
        Test against the second general example provided at
        http://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm
        """
        self.assertEqual(['m', 'i', 'i', 'm', 's', 'm', 'm', 'm'],
                         algorithms.native_align('sunday', 'saturday'))


class SemiGlobalAlignmentTests(unittest.TestCase):

    """
    Tests the semi_global_align function.
    """

    def test_sequence_length_inversion(self):
        """
        Test that an exception is thrown if the first sequence is > the second.
        """
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.native_semi_global_align, 'abcdefghi', '')
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.native_semi_global_align, 'a', '')
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.native_semi_global_align, ['word'], [])
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.native_semi_global_align, ['word1',
                                                                'word2',
                                                                'word3'],
                          ['word'])

    def test_identical(self):
        """
        Test with strings and lists of equal length.
        """
        expected = ['m']
        self.assertEqual(
            expected, algorithms.native_semi_global_align('a', 'a'))
        self.assertEqual(
            expected, algorithms.native_semi_global_align(['a'], ['a']))

    def test_identical_long(self):
        """
        Test with a longer series of matches.
        """
        expected = ['m', 'm', 'm', 'm', 'm']
        self.assertEqual(
            expected, algorithms.native_semi_global_align('abcde', 'abcde'))

    def test_identical_words(self):
        """
        Test with a series of of matching words.
        """
        expected = ['m', 'm', 'm', 'm', 'm']
        self.assertEqual(expected, algorithms.native_semi_global_align(
            ['word1', 'word2', 'word3', 'word4', 'word5'], ['word1', 'word2',
                                                            'word3', 'word4',
                                                            'word5']))

    def test_simple_prefix(self):
        """
        Test with a single match and a skippable prefix.
        """
        expected = ['i', 'i', 'i', 'i', 'm']
        self.assertEqual(
            expected, algorithms.native_semi_global_align('b', 'aaaab'))

    def test_prefix_with_trailer(self):
        """
        Test with a single match and a skippable prefix and trailer.
        """
        expected = ['i', 'i', 'i', 'i', 'm']
        self.assertEqual(
            expected, algorithms.native_semi_global_align('b', 'aaaabcccc'))

    def test_word_prefix(self):
        """
        Test a list of words with a prefix.
        """
        expected = ['i', 'i', 'm']
        self.assertEqual(expected, algorithms.native_semi_global_align(
            ['match'], ['w1', 'w2', 'match']))


class NumpyLevenshteinTests(unittest.TestCase):

    """
    Tests the np_full_edit_distance funtion by checking both the edit distance
    and full matrix comparisons.
    """
    # -------------------------------------------------------------------
    # Edit distance tests -----------------------------------------------
    # -------------------------------------------------------------------

    def test_equal_strings(self):
        """
        Test the edit distance of identical strings
        """
        self.assertEqual(0, algorithms.np_full_edit_distance(
            'test_string', 'test_string')[0][-1, -1])

    def test_single_insert(self):
        """
        Test with strings requiring one insert
        """
        self.assertEqual(1, algorithms.np_full_edit_distance('', 'a')[0][-1,
                                                                         -1])

    def test_tenfold_insert(self):
        """
        Test with strings requiring ten inserts
        """
        self.assertEqual(10, algorithms.np_full_edit_distance(
            '', 'aaaaaaaaaa')[0][-1, -1])  # A string with 10 a's.

    def test_single_delete(self):
        """
        Test with strings requiring one delete
        """
        self.assertEqual(
            1, algorithms.np_full_edit_distance('a', '')[0][-1, -1])

    def test_tenfold_delete(self):
        """
        Test with strings requiring ten deletes
        """
        self.assertEqual(10, algorithms.np_full_edit_distance(
            'aaaaaaaaaa', '')[0][-1, -1])  # A string with 10 a's.

    def test_singledelete_singleadd(self):
        """
        Test with strings requiring a single non-trivial insert.
        """
        self.assertEqual(2, algorithms.np_full_edit_distance('abbb',
                                                             'bbbbb')[0][-1,
                                                                         -1])

    def test_singleadd_singledelete(self):
        """
        Test with strings requiring a single non-trivial delete.
        """
        self.assertEqual(2, algorithms.np_full_edit_distance('bbbbb',
                                                             'abbb')[0][-1,
                                                                        -1])
    # -------------------------------------------------------------------
    # Score matrix tests ------------------------------------------------
    # -------------------------------------------------------------------

    def test_match_delete_matrix(self):
        """
        Test the scoring matrix state in an edit requiring one match and
        delete.
        """
        expected = numpy.array([[0, 1, 2], [1, 0, 1]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('a',
                                                                           'ab')[0]))

    def test_match_insert_matrix(self):
        """
        Test the scoring matrix state in an edit requiring one match an insert.
        """
        expected = numpy.array([[0, 1], [1, 0], [2, 1]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('ab',
                                                                           'a')[0]))

    def test_all_match_matrix(self):
        """
        Test the scoring matrix state in an edit consisting only of multiple
        matches.
        """
        expected = numpy.array([[0, 1, 2, 3, 4, 5],
                                [1, 0, 1, 2, 3, 4],
                                [2, 1, 0, 1, 2, 3],
                                [3, 2, 1, 0, 1, 2],
                                [4, 3, 2, 1, 0, 1],
                                [5, 4, 3, 2, 1, 0]])
        self.assertTrue(numpy.array_equal(
            expected, algorithms.np_full_edit_distance('aaaaa', 'aaaaa')[0]))

    def test_all_subtitute_matrix(self):
        """
        Test the scoring matrix state in an edit consisting only of multiple
        substitutes.
        """
        expected = numpy.array([[0, 1, 2, 3, 4, 5],
                                [1, 1, 2, 3, 4, 5],
                                [2, 2, 2, 3, 4, 5],
                                [3, 3, 3, 3, 4, 5],
                                [4, 4, 4, 4, 4, 5],
                                [5, 5, 5, 5, 5, 5]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('aaaaa',
                                                                           'bbbbb')[0]))

    def test_all_insert(self):
        """
        Test the scoring matrix state in an edit consisting only of multiple
        inserts.
        """
        expected = numpy.array([[0, 1, 2, 3, 4, 5]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('',
                                                                           'abcde')[0]))

    def test_all_delete(self):
        """
        Test the scoring matrix state in an edit consisting only of deletes.
        """
        expected = numpy.array([[0],
                                [1],
                                [2],
                                [3],
                                [4],
                                [5]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('abcde',
                                                                           '')[0]))

    def test_all_empty(self):
        """
        Test the scoring matrix state in an edit between two empty strings.
        """
        expected = numpy.zeros(shape=(1, 1))
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('',
                                                                           '')[0]))
    # -------------------------------------------------------------------
    # Parameter tests ---------------------------------------------------
    # -------------------------------------------------------------------

    def test_substitution_parameter(self):
        """
        Test the functionality of the substitution score parameter.
        """
        default = algorithms.np_full_edit_distance('a', 'b')[0][-1, -1]
        same_as_default = algorithms.np_full_edit_distance(
            'a', 'b', substitutionscore=1)[0][-1, -1]
        with_parameter = algorithms.np_full_edit_distance(
            'a', 'b', substitutionscore=-7)[0][-1, -1]
        with_parameter_and_max = algorithms.np_full_edit_distance(
            'a', 'b', substitutionscore=7)[0][-1, -1]
        self.assertEqual(1, default)
        self.assertEqual(1, same_as_default)
        self.assertEqual(-7, with_parameter)

    def test_deletion_parameter(self):
        """
        Test the functionality of the delete score parameter.
        """
        default = algorithms.np_full_edit_distance('a', '')[0][-1, -1]
        same_as_default = algorithms.np_full_edit_distance(
            'a', '', deletescore=1)[0][-1, -1]
        with_parameter = algorithms.np_full_edit_distance(
            'a', '', deletescore=-7)[0][-1, -1]

        self.assertEqual(1, default)
        self.assertEqual(1, same_as_default)
        self.assertEqual(-7, with_parameter)

    def test_insertion_parameter(self):
        """
        Test the functionality of the insert score parameter.
        """
        default = algorithms.np_full_edit_distance('', 'a')[0][-1, -1]
        same_as_default = algorithms.np_full_edit_distance(
            '', 'a', insertscore=1)[0][-1, -1]
        with_parameter = algorithms.np_full_edit_distance(
            '', 'a', insertscore=-7)[0][-1, -1]

        self.assertEqual(1, default)
        self.assertEqual(1, same_as_default)
        self.assertEqual(-7, with_parameter)

    def test_charmatrix_one_character_substitution_lower(self):
        """
        Test the functionality of the charmatrix parameter where in reduces the
        score of a substitution.
        """
        charmatrix = {('a', 'b'): 0}
        expected = numpy.array([[0, 1],
                                [1, 0]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('a',
                                                                           'b',
                                                                           charmatrix=charmatrix)[0]))

    def test_charmatrix_one_character_substitution_higher(self):
        """
        Test the functionality of the charmatrix parameter where in increases
        the score of a substitution.
        """
        charmatrix = {('a', 'b'): 5}
        expected = numpy.array([[0, 1],
                                [1, 5]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('a',
                                                                           'b',
                                                                           charmatrix=charmatrix)[0]))

    def test_charmatrix_one_character_substitution_default(self):
        """
        Test the functionality of the charmatrix parameter where it does not
        change a character score.
        """
        charmatrix = {('a', 'b'): 1}
        expected = numpy.array([[0, 1],
                                [1, 1]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('a',
                                                                           'b',
                                                                           charmatrix=charmatrix)[0]))

    def test_charmatrix_default_delete(self):
        """
        Test the case where the charmatrix mutates the score of trivial (first
        column) deletes.
        """
        charmatrix = {('', 'a'): 5}
        expected = numpy.array([[0],
                                [5],
                                [10],
                                [15]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('aaa',
                                                                           '',
                                                                           charmatrix=charmatrix)[0]))

    def test_charmatrix_default_insert(self):
        """
        Test the case where the charmatrix mutates the score of trivial (first
        row) inserts.
        """
        charmatrix = {('a', ''): 5}
        expected = numpy.array([[0, 5, 10, 15]])
        self.assertTrue(numpy.array_equal(expected,
                                          algorithms.np_full_edit_distance('',
                                                                           'aaa',
                                                                           charmatrix=charmatrix)[0]))
    # -------------------------------------------------------------------
    # Word tests --------------------------------------------------------
    # -------------------------------------------------------------------

    def test_identical_word(self):
        self.assertEqual(0, algorithms.np_full_edit_distance(['word'],
                                                             ['word'])[0][-1,
                                                                          -1])

    def test_word_substitution(self):
        self.assertEqual(1, algorithms.np_full_edit_distance(['word'],
                                                             ['different\
                                                              word'])[0][-1,
                                                                         -1])

    def test_word_insertion(self):
        self.assertEqual(1, algorithms.np_full_edit_distance([],
                                                             ['word'])[0][-1,
                                                                          -1])

    def test_word_deletion(self):
        self.assertEqual(1, algorithms.np_full_edit_distance(['word'],
                                                             [])[0][-1, -1])

    def test_word_multi_insert(self):
        self.assertEqual(5, algorithms.np_full_edit_distance([], ['word',
                                                                  'word',
                                                                  'word',
                                                                  'word',
                                                                  'word'])[0][-1,
                                                                              -1])

    def test_word_multi_delete(self):
        self.assertEqual(5, algorithms.np_full_edit_distance(
            ['word', 'word', 'word', 'word', 'word'], [])[0][-1, -1])

    def test_word_multi_match(self):
        self.assertEqual(0, algorithms.np_full_edit_distance(
            ['word1', 'word2', 'word3'], ['word1', 'word2', 'word3'])[0][-1, -1])

    def test_word_multi_substitute(self):
        self.assertEqual(3, algorithms.np_full_edit_distance(
            ['word1', 'word2', 'word3'], ['otherword1', 'otherword2', 'otherword3'])[0][-1, -1])


class NumpyAlignmentTests(unittest.TestCase):

    def test_empty_strings(self):
        """
        Tests the edit steps between two empty strings.
        """
        self.assertEqual([], algorithms.np_align('', ''))

    def test_insertions(self):
        """
        Test the edit steps when only inserts are needed.
        """
        self.assertEqual(['i', 'i', 'i', 'i', 'i'],
                         algorithms.np_align('', 'abcde'))

    def test_deletions(self):
        """
        Test the edit steps when only deletes are needed.
        """
        self.assertEqual(['d', 'd', 'd', 'd', 'd'],
                         algorithms.np_align('abcde', ''))

    def test_matches(self):
        """
        Test the edit steps when only matches are needed.
        """
        self.assertEqual(['m', 'm', 'm', 'm', 'm'],
                         algorithms.np_align('abcde', 'abcde'))

    def test_matches_1(self):  # TODO
        """
        Test the edit steps when only substitutions are needed.
        """
        self.assertEqual(['s', 's', 's', 's', 's'],
                         algorithms.np_align('abcde', 'vwxyz'))

    def test_wikipedia_example_1(self):
        """
        Test against the first general example provided at
        http://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm
        """
        self.assertEqual(['s', 'm', 'm', 'm', 's', 'm', 'd'],
                         algorithms.np_align('sitting', 'kitten'))

    def test_wikipedia_example_2(self):
        """
        Test against the second general example provided at
        http://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm
        """
        self.assertEqual(['m', 'i', 'i', 'm', 's', 'm', 'm', 'm'],
                         algorithms.np_align('sunday', 'saturday'))
    # -------------------------------------------------------------------
    # Word Alignment Tests ----------------------------------------------
    # -------------------------------------------------------------------

    def test_empty_word_list(self):
        """
        Tests the edit steps between two empty lists.
        """
        self.assertEqual([], algorithms.np_align([], []))

    def test_word_insertions(self):
        """
        Test the edit steps when only inserts are needed.
        """
        self.assertEqual(['i', 'i', 'i', 'i', 'i'], algorithms.np_align(
            [], ['word1', 'word2', 'word3', 'word4', 'word5']))

    def test_word_deletions(self):
        """
        Test the edit steps when only inserts are needed.
        """
        self.assertEqual(['d', 'd', 'd', 'd', 'd'], algorithms.np_align(
            ['word1', 'word2', 'word3', 'word4', 'word5'], []))

    def test_word_matches(self):
        """
        Test the edit steps when only matches are needed.
        """
        self.assertEqual(['m', 'm', 'm', 'm', 'm'], algorithms.np_align(
            ['word1', 'word2', 'word3', 'word4', 'word5'], ['word1', 'word2', 'word3', 'word4', 'word5']))


class NumpySemiGlobalAlignmentTests(unittest.TestCase):

    """
    Tests the np_semi_global_align function.
    """

    def test_sequence_length_inversion(self):
        """
        Test that an exception is thrown if the first sequence is > the second.
        """
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.np_semi_global_align, 'abcdefghi', '')
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.np_semi_global_align, 'a', '')
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.np_semi_global_align, ['word'], [])
        self.assertRaises(NidabaAlgorithmException,
                          algorithms.np_semi_global_align, ['word1', 'word2',
                                                            'word3'], ['word'])

    def test_identical(self):
        """
        Test with strings and lists of equal length.
        """
        expected = ['m']
        self.assertEqual(expected, algorithms.np_semi_global_align('a', 'a'))
        self.assertEqual(expected, algorithms.np_semi_global_align(['a'],
                                                                   ['a']))

    def test_identical_long(self):
        """
        Test with a longer series of matches.
        """
        expected = ['m', 'm', 'm', 'm', 'm']
        self.assertEqual(expected, algorithms.np_semi_global_align('abcde',
                                                                   'abcde'))

    def test_identical_words(self):
        """
        Test with a series of of matching words.
        """
        expected = ['m', 'm', 'm', 'm', 'm']
        self.assertEqual(expected, algorithms.np_semi_global_align(['word1',
                                                                    'word2',
                                                                    'word3',
                                                                    'word4',
                                                                    'word5'],
                                                                   ['word1',
                                                                    'word2',
                                                                    'word3',
                                                                    'word4',
                                                                    'word5']))

    def test_simple_prefix(self):
        """
        Test with a single match and a skippable prefix.
        """
        expected = ['i', 'i', 'i', 'i', 'm']
        self.assertEqual(expected, algorithms.np_semi_global_align('b',
                                                                   'aaaab'))

    def test_prefix_with_trailer(self):
        """
        Test with a single match and a skippable prefix and trailer.
        """
        expected = ['i', 'i', 'i', 'i', 'm']
        self.assertEqual(expected, algorithms.np_semi_global_align('b',
                                                                   'aaaabcccc'))

    def test_word_prefix(self):
        """
        Test a list of words with a prefix.
        """
        expected = ['i', 'i', 'm']
        self.assertEqual(expected, algorithms.np_semi_global_align(['match'],
                                                                   ['w1', 'w2',
                                                                    'match']))

# ----------------------------------------------------------------------
# Language Tests -------------------------------------------------------
# ----------------------------------------------------------------------


class LanguageTests(unittest.TestCase):

    def test_unibarrier_arg_raise(self):
        """
        Tests that the proper exception is throw if an arg of type str
        is passed in.
        """

        @algorithms.unibarrier
        def dummyfunction(*args, **kwargs):
            pass

        self.assertRaises(NidabaUnibarrierException,
                          dummyfunction, str('a string'))

        self.assertRaises(NidabaUnibarrierException,
                          dummyfunction,
                          str('a string'),
                          str('another string'))

        self.assertRaises(NidabaUnibarrierException,
                          dummyfunction,
                          str('100 of me!') * 100, u'I donn\'t matter')

    def test_unibarrier_kwarg_raise(self):
        """
        Tests that the proper exception is throw if an kwarg of type str
        is passed in.
        """

        @algorithms.unibarrier
        def dummyfunction(*args, **kwargs):
            pass

        self.assertRaises(NidabaUnibarrierException, dummyfunction,
                          kw1=str('a string'))

        self.assertRaises(NidabaUnibarrierException, dummyfunction,
                          kw1=str('a string'), kw2=str('another string'))

        self.assertRaises(NidabaUnibarrierException, dummyfunction,
                          largekw=str('100 of me!') * 100)

        self.assertRaises(NidabaUnibarrierException, dummyfunction,
                          largekw=str('100 of me!') * 100, kw=u'I don\'t matter')

    def test_unibarrier_passthrough(self):
        """
        Test that args and kwargs of type unicode do not cause an
        exception to be raised.
        """

        @algorithms.unibarrier
        def dummyfunction(*args, **kwargs):
            pass

        try:
            dummyfunction()
            dummyfunction(u'a unicode arg')
            dummyfunction(u'a unicode arg', u'another uni arg')
            dummyfunction(kw1=u'a unicode kwarg')
            dummyfunction(kw1=u'a unicode kwarg', kw2=u'another unicode kwarg')
            dummyfunction(u'a unicode arg', u'another uni arg', kw1=u'a unicode\
                          kwarg', kw2=u'another unicode kwarg')
        except NidabaUnibarrierException:
            self.fail()

    def test_inblock(self):
        """
        Tests the inblock function using the printable part of the ascii
        block. This block was chosen arbitrarily.
        """
        asciistr = (u"""!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUV"""
                    """WXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~""")
        for c in asciistr:
            self.assertTrue(algorithms.inblock(c, ('!', '~')))

        self.assertFalse(algorithms.inblock(unichr(ord('!') - 1), ('!', '~')))
        self.assertFalse(algorithms.inblock(unichr(ord('~') + 1), ('!', '~')))

    def test_identify_all_ascii_simple(self):
        """
        Test the text identify method against the ascii unicode block.
        """
        asciistr = (u'ascii', unichr(0), unichr(127))
        ex1 = algorithms.identify(u'this is a string of ascii', [asciistr])
        self.assertEqual(ex1, {u'ascii': 25})

    def test_identify_all_ascii(self):
        """
        Test the text identify method against the ascii unicode block.
        """
        asciistr = (u'ascii', unichr(0), unichr(127))

        for i in xrange(0, 128):
            self.assertEqual(
                {u'ascii': 1}, algorithms.identify(unichr(i), [asciistr]))

    def test_identify_greek_and_latin(self):
        """
        Test the identify method on a string that contains both greek
        and latin characters.
        """
        greek = (u'Greek Coptic', u'\u0370', u'\u03FF')

        self.assertEqual({greek[0]: len(u'Σωκράτης')},
                         algorithms.identify(u'Σωκράτης', [greek]))
        self.assertEqual({greek[0]: len(u'Πλάτων')},
                         algorithms.identify(u'Πλάτων', [greek]))

    def test_is_lang_threshhold_check(self):
        """
        Test that an exception is raised if an invalid threshold value
        is entered.
        """
        self.assertRaises(Exception, algorithms.islang, None, None, -0.00001)
        self.assertRaises(Exception, algorithms.islang, None, None, 1.00001)
        self.assertRaises(Exception, algorithms.islang, None, None, 0.0)

    def test_is_lang_100percent_ascii(self):
        """
        Test with a pure ascii string.
        """
        asciistr = (u"""!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUV
                     WXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~""")
        self.assertTrue(algorithms.islang(asciistr, [algorithms.ascii_range]))

    def test_is_lang_100percent_greek(self):
        """
        Test with two strings containing characters from the Greek and
        Coptic block.
        """
        gk1 = u'Σωκράτης'
        gk2 = u'Πλάτων'
        self.assertTrue(
            algorithms.islang(gk1, [algorithms.greek_coptic_range]))
        self.assertTrue(
            algorithms.islang(gk2, [algorithms.greek_coptic_range]))

    def test_is_lang_50percent_greekascii(self):
        """
        Test with a string that is half ascii and half Greek and Coptic.
        """
        halfandhalf = u'Πλάτων_ascii'
        self.assertTrue(algorithms.islang(halfandhalf,
                                          [algorithms.ascii_range],
                                          threshold=0.5))
        self.assertTrue(algorithms.islang(halfandhalf,
                                          [algorithms.greek_coptic_range],
                                          threshold=0.5))

        self.assertFalse(algorithms.islang(halfandhalf,
                                           [algorithms.greek_coptic_range],
                                           threshold=0.5000001))
        self.assertFalse(algorithms.islang(halfandhalf,
                                           [algorithms.greek_coptic_range],
                                           threshold=0.5000001))

    def test_isgreek(self):
        """
        Test the isgreek convenience function.
        """
        gk1 = u'Σωκράτης'
        gk2 = u'Πλάτων'
        self.assertTrue(algorithms.isgreek(gk1))
        self.assertTrue(algorithms.isgreek(gk2))

    def test_sanitize_strip(self):
        """
        Test that sanitize correctly strips leading and trailing whitespace.
        """
        s = u'\n\t abcde \n\t fghij \n\t'
        self.assertEqual(u'abcde \n\t fghij', algorithms.sanitize(s))

    def test_sanitize_NFD_decompose(self):
        """
        Test that sanitize correctly converts to NFD codepoints.
        """
        # Small alpha with a tone mark
        alpha = u'\u03AC'
        self.assertNotEqual(alpha, algorithms.sanitize(alpha))
        self.assertEqual(u'\u03B1' + u'\u0301', algorithms.sanitize(alpha))

        # Greek small letter upsilon with dialytika and tonos
        upsilon = u'\u03B0'
        self.assertNotEqual(upsilon, algorithms.sanitize(upsilon))
        self.assertEqual(u'\u03C5' + u'\u0308' + u'\u0301',
                         algorithms.sanitize(upsilon))

    def test_sanitize_NFC(self):
        """
        Test that sanitize correctly converts to NFC codepoints.
        """
        decomp_alpha = u'\u03B1' + u'\u0301'
        self.assertNotEqual(decomp_alpha, algorithms.sanitize(decomp_alpha,
                                                              normalization=u'NFC'))
        self.assertEqual(u'\u03AC', algorithms.sanitize(decomp_alpha,
                                                        normalization=u'NFC'))

        decomp_upsilon = u'\u03C5' + u'\u0308' + u'\u0301'
        self.assertNotEqual(decomp_upsilon, algorithms.sanitize(decomp_upsilon,
                                                                normalization=u'NFC'))
        self.assertEqual(
            u'\u03B0', algorithms.sanitize(decomp_upsilon, normalization=u'NFC'))

    def test_sanitize_decode(self):
        """
        Test that strings are converted to unicode correctly.
        """
        utf8 = u'I contain a non-ascii character: \u03B1'.encode(u'utf-8')
        utf16 = u'I contain a non-ascii character: \u03B1'.encode(u'utf-16')
        utf32 = u'I contain a non-ascii character: \u03B1'.encode(u'utf-32')
        expected = u'I contain a non-ascii character: \u03B1'
        self.assertEqual(expected, algorithms.sanitize(utf8))
        self.assertEqual(
            expected, algorithms.sanitize(utf16, encoding=u'utf-16'))
        self.assertEqual(
            expected, algorithms.sanitize(utf32, encoding=u'utf-32'))

    def test_diacritic_strip_combining(self):
        """
        Tests the strip_diacritic fuction on the combining diacritics
        unicode block.
        """
        cd = algorithms.combining_diacritical_mark_range
        diacritics = algorithms.uniblock(cd[1], cd[2])
        self.assertNotEqual(len(diacritics), 0)
        self.assertEqual(u'', algorithms.strip_diacritics(diacritics))

    def test_diacritic_strip_noncombining(self):
        """
        Test the strip_diacritic function on all the diacritics not in
        the combining diacritical range.
        """
        gc_diacritics = u'ͺ΄΅'
        gx_diacritics = u'᾽ι᾿῀῁῍῎῏῝῟῞῭΅`´῾'
        diacritics = gc_diacritics + gx_diacritics
        self.assertNotEqual(len(diacritics), 0)
        self.assertEqual(u'', algorithms.strip_diacritics(diacritics))

# ----------------------------------------------------------------------
# Symmetric spell check tests ------------------------------------------
# ----------------------------------------------------------------------


class SymSpellTests(unittest.TestCase):

    def test_strings_by_deletion_1(self):
        """
        Test the strings_by_deletion function with one delete.
        """
        expected = [u'abcd', u'abce', u'abde', u'acde', u'bcde']
        self.assertEqual(expected, algorithms.strings_by_deletion(u'abcde', 1))

    def test_strings_by_deletion_2(self):
        """
        Test the strings_by_deletion function with two deletes.
        """
        expected = [u'a', u'e', u'p']
        self.assertEqual(expected, algorithms.strings_by_deletion(u'ape', 2))

    def test_strings_bzy_deletion_exceed(self):
        """
        Test the strings_by_deletion function where the number of
        deletes exceeds characters in the string.
        """
        self.assertEqual([], algorithms.strings_by_deletion(u'aaa', 10))

    def test_sym_suggest_already_word(self):
        """
        Test sym_suggest in the case where the specified string is
        already a word in the dictionary.
        """
        delete_dic = {u'ord': [u'word'], u'wod': [u'word'], u'wor': [u'word'],
                      u'wrd': [u'word'], u'ree': [u'tree'], u'tee': [u'tree'],
                      u'tre': [u'tree']}
        dic = {u'tree', u'word'}
        # delete_dic = {u'word':[u'ord', u'wod', u'wor', u'wrd'],
        #        u'tree':[u'ree', u'tee', u'tre']}

        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'word', dic, delete_dic, 1))
        self.assertEqual(
            [u'tree'], algorithms.sym_suggest(u'tree', dic, delete_dic, 1))

    def test_sym_suggest_single_delete(self):
        """
        Test sym_suggest where the string differs from words by a
        single delete.
        """
        delete_dic = {u'ord': [u'word'], u'wod': [u'word'], u'wor': [u'word'],
                      u'wrd': [u'word'], u'ree': [u'tree'], u'tee': [u'tree'],
                      u'tre': [u'tree']}
        dic = {u'tree', u'word'}

        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'ord', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'wod', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'wor', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'wrd', dic, delete_dic, 1))

    def test_sym_suggest_single_insert(self):
        """
        Test sym_suggest where the string differs from words by a single
        insert.
        """
        delete_dic = {u'Xword': [u'word'], u'wXord': [u'word'], u'woXrd':
                      [u'word'], u'worXd': [u'word'], u'wordX': [u'word'],
                      u'Xtree': [u'tree']}
        dic = {u'tree', u'word'}

        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'Xword', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'wXord', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'woXrd', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'worXd', dic, delete_dic, 1))
        self.assertEqual(
            [u'word'], algorithms.sym_suggest(u'wordX', dic, delete_dic, 1))
        self.assertEqual(
            [u'tree'], algorithms.sym_suggest(u'Xtree', dic, delete_dic, 1))

    def test_sym_suggest_single_substitution(self):
        """
        Test sym_suggest where the string differs from words by a single
        insert.
        """
        delete_dic = {u'Word': [u'word'], u'wOrd': [
            u'word'], u'woRd': [u'word'], u'worD': [u'word']}
        dic = {u'word'}

        self.assertEqual([u'word'], algorithms.sym_suggest(u'Word', dic,
                                                           delete_dic, 1))
        self.assertEqual([u'word'], algorithms.sym_suggest(u'wOrd', dic,
                                                           delete_dic, 1))
        self.assertEqual([u'word'], algorithms.sym_suggest(u'woRd', dic,
                                                           delete_dic, 1))
        self.assertEqual([u'word'], algorithms.sym_suggest(u'worD', dic,
                                                           delete_dic, 1))

    def test_string_compare(self):
        """
        Test the string comparison function.
        """
        self.assertEqual(1, algorithms.compare_strings(u'a', u'b'))
        self.assertEqual(-1, algorithms.compare_strings(u'b', u'a'))
        self.assertEqual(0, algorithms.compare_strings(u'a', u'a'))
        self.assertEqual(1, algorithms.compare_strings(u'a', u'aaaaa'))
        self.assertEqual(-1, algorithms.compare_strings(u'aaaaa', u'a'))

    def test_previous_newline_no_newline(self):
        """
        Test the previous newline function when it should move to the
        beginning of the file.
        """
        df = tempfile.NamedTemporaryFile()
        df.write(u'abc')
        df.seek(0, 0)
        with open(os.path.abspath(df.name), 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0)
            self.assertEqual(0, algorithms.prev_newline(mm, 50))
        df.close()

    def test_previous_newline_single_overflow(self):
        """
        Test the previous newline function.
        """
        df = tempfile.NamedTemporaryFile()
        df.write(u'abc\ndef')
        df.seek(0, 0)
        with open(os.path.abspath(df.name), 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0)
            # Test the points to the left of the newline character
            mm.seek(0)
            self.assertEqual(0, algorithms.prev_newline(mm, 50))
            mm.seek(1)
            self.assertEqual(0, algorithms.prev_newline(mm, 50))
            mm.seek(2)
            self.assertEqual(0, algorithms.prev_newline(mm, 50))
            mm.seek(3)
            self.assertEqual(0, algorithms.prev_newline(mm, 50))

            # Test the points to the right of the newline character
            mm.seek(4)
            self.assertEqual(4, algorithms.prev_newline(mm, 50))
            mm.seek(5)
            self.assertEqual(4, algorithms.prev_newline(mm, 50))
            mm.seek(6)
            self.assertEqual(4, algorithms.prev_newline(mm, 50))
            mm.seek(7)
            self.assertEqual(4, algorithms.prev_newline(mm, 50))
        df.close()

    def test_previous_newline_multiple_left(self):
        """
        Test the prev_newline function when it would pass several
        newlines.
        """
        df = tempfile.NamedTemporaryFile()
        df.write(u'abcde\nfghijk\nlmnopq\nrstuv\nwxyz')
        df.seek(0, 0)
        with open(os.path.abspath(df.name), 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0)
            mm.seek(30)
            self.assertEqual(26, algorithms.prev_newline(mm, 50))
        df.close()

    def test_key_for_delete_dict_entry(self):
        """
        Tests the key_for_del_dict_entry function.
        """
        single_entry = u'key\tval1'
        multiple_entries = u'key\tval1 val2 val3'
        self.assertEqual((u'key', u'val1'),
                         algorithms.key_for_del_dict_entry(single_entry))
        self.assertEqual((u'key', u'val1 val2 val3'),
                         algorithms.key_for_del_dict_entry(multiple_entries))

    def test_key_for_single_word(self):
        """
        Tests the test_key_for_single_word function.
        """
        w1 = u'word1'
        w2 = u'word2'
        w3 = u'word3'
        self.assertEqual(
            (u'word1', u'word1'), algorithms.key_for_single_word(w1))
        self.assertEqual(
            (u'word2', u'word2'), algorithms.key_for_single_word(w2))
        self.assertEqual(
            (u'word3', u'word3'), algorithms.key_for_single_word(w3))

    def test_mmap_bin_search_single(self):
        """
        Tests the mmap_bin_search algorithm with a dictionary with
        one item.
        """
        df = tempfile.NamedTemporaryFile()
        df.write(u'only_entry\tsome_value')
        df.seek(0, 0)
        with open(os.path.abspath(df.name), 'r+b') as f:
            mmap.mmap(f.fileno(), 0)
            expected = u'some_value'
            dpath = os.path.abspath(df.name).decode(u'utf-8')
            self.assertEqual(expected,
                             algorithms.mmap_bin_search(u'only_entry', dpath))

    def test_mmap_bin_search_double(self):
        """
        Tests the mmap_bin_search algorithm with a dictionary with
        two items.
        """
        df = tempfile.NamedTemporaryFile()
        df.write(u'first_key\tfirst_value\n')
        df.write(u'second_key\tsecond_value')
        df.seek(0, 0)
        with open(os.path.abspath(df.name), 'r+b') as f:
            mmap.mmap(f.fileno(), 0)
            expected_first = u'first_value'
            expected_second = u'second_value'
            dpath = os.path.abspath(df.name).decode(u'utf-8')
            self.assertEqual(expected_first,
                             algorithms.mmap_bin_search(u'first_key', dpath))
            self.assertEqual(expected_second,
                             algorithms.mmap_bin_search(u'second_key', dpath))

    def test_mmap_bin_search_general(self):
        """
        Test the mmap_bin_search function in a general case.
        """
        df = tempfile.NamedTemporaryFile()
        df.write('akey\taval\n')
        df.write('bkey\tbval\n')
        df.write('ckey\tcval\n')
        df.write('dkey\tdval\n')
        df.write('ekey\teval\n')
        df.write('fkey\tfval\n')
        df.seek(0, 0)
        dpath = os.path.abspath(df.name).decode(u'utf-8')
        ex_a = u'aval'
        ex_b = u'bval'
        ex_c = u'cval'
        ex_d = u'dval'
        ex_e = u'eval'
        ex_f = u'fval'
        self.assertEqual(ex_a, algorithms.mmap_bin_search(u'akey', dpath))
        self.assertEqual(ex_b, algorithms.mmap_bin_search(u'bkey', dpath))
        self.assertEqual(ex_c, algorithms.mmap_bin_search(u'ckey', dpath))
        self.assertEqual(ex_d, algorithms.mmap_bin_search(u'dkey', dpath))
        self.assertEqual(ex_e, algorithms.mmap_bin_search(u'ekey', dpath))
        self.assertEqual(ex_f, algorithms.mmap_bin_search(u'fkey', dpath))
        self.assertEqual(None, algorithms.mmap_bin_search(u'gkey', dpath))

    def test_mmap_simple_single_word(self):
        """
        Test the mmap_bin_search function for accessing words from a
        simple word-per-line dictionary.
        """
        df = tempfile.NamedTemporaryFile()
        df.write('aval\n')
        df.write('bval\n')
        df.write('cval\n')
        df.write('dval\n')
        df.seek(0, 0)
        dpath = os.path.abspath(df.name).decode(u'utf-8')
        ex_a = u'aval'
        ex_b = u'bval'
        ex_c = u'cval'
        ex_d = u'dval'
        self.assertEqual(ex_a,
                         algorithms.mmap_bin_search(u'aval', dpath,
                                                    entryparser_fn=algorithms.key_for_single_word))
        self.assertEqual(ex_b,
                         algorithms.mmap_bin_search(u'bval', dpath,
                                                    entryparser_fn=algorithms.key_for_single_word))
        self.assertEqual(ex_c,
                         algorithms.mmap_bin_search(u'cval', dpath,
                                                    entryparser_fn=algorithms.key_for_single_word))
        self.assertEqual(ex_d,
                         algorithms.mmap_bin_search(u'dval', dpath,
                                                    entryparser_fn=algorithms.key_for_single_word))


class SpellCheckTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile()
        self.temp.write(u'123\t1234\n')
        self.temp.write(u'124\t1234\n')
        self.temp.write(u'134\t1234\n')
        self.temp.write(u'234\t1234\n')
        self.temp.write(u'aaaa\taaaaa\n')
        self.temp.write(u'bbbb\tbbbbb\n')
        self.temp.seek(0, 0)

        self.dic = set()
        self.dic.add(u'aaaaa')
        self.dic.add(u'bbbbb')
        self.dic.add(u'1234')

    def tearDown(self):
        self.temp.close()

    def test_suggest_empty_string_1(self):
        """
        Test the spelling suggestor with an empty input string
        """
        result = algorithms.mapped_sym_suggest(u'',
                                               self.temp.name.decode('utf-8'),
                                               self.dic, 1)
        self.assertEqual(len(result[u'ins']), 0)
        self.assertEqual(len(result[u'dels']), 0)
        self.assertEqual(len(result[u'subs']), 0)
        self.assertEqual(len(result[u'ins+dels']), 0)

    def test_suggest_1_insert(self):
        """
        Test the spellchecker in the case of a single insert.
        """
        result_a = algorithms.mapped_sym_suggest(u'aaaa',
                                                 self.temp.name.decode(
                                                     'utf-8'),
                                                 self.dic, 1)
        result_b = algorithms.mapped_sym_suggest(u'bbbb',
                                                 self.temp.name.decode(
                                                     'utf-8'),
                                                 self.dic, 1)
        self.assertEqual(len(result_a[u'ins']), 1)
        self.assertEqual(len(result_a[u'dels']), 0)
        self.assertEqual(len(result_a[u'subs']), 0)
        self.assertEqual(len(result_a[u'ins+dels']), 0)
        self.assertEqual(len(result_b[u'ins']), 1)
        self.assertEqual(len(result_b[u'dels']), 0)
        self.assertEqual(len(result_b[u'subs']), 0)
        self.assertEqual(len(result_b[u'ins+dels']), 0)

    def test_suggest_1_delete(self):
        """
        Test the spellchecker in the case of a single delete.
        """
        result_a = algorithms.mapped_sym_suggest(u'aaXaaa',
                                                 self.temp.name.decode(
                                                     'utf-8'),
                                                 self.dic, 1)
        result_b = algorithms.mapped_sym_suggest(u'Xbbbbb',
                                                 self.temp.name.decode(
                                                     'utf-8'),
                                                 self.dic, 1)

        self.assertEqual(len(result_a[u'ins']), 0)
        self.assertEqual(len(result_a[u'dels']), 1)
        self.assertEqual(len(result_a[u'subs']), 0)
        self.assertEqual(len(result_a[u'ins+dels']), 0)

        self.assertEqual(len(result_b[u'ins']), 0)
        self.assertEqual(len(result_b[u'dels']), 1)
        self.assertEqual(len(result_b[u'subs']), 0)
        self.assertEqual(len(result_b[u'ins+dels']), 0)

    def test_suggest_1_substitute(self):
        """
        Test the spellchecker in the case of a single substitution.
        """
        result_a = algorithms.mapped_sym_suggest(u'aaXaa',
                                                 self.temp.name.decode(
                                                     'utf-8'),
                                                 self.dic, 1)
        result_b = algorithms.mapped_sym_suggest(u'Xbbbb',
                                                 self.temp.name.decode(
                                                     'utf-8'),
                                                 self.dic, 1)

        self.assertEqual(len(result_a[u'ins']), 0)
        self.assertEqual(len(result_a[u'dels']), 0)
        self.assertEqual(len(result_a[u'subs']), 1)
        self.assertEqual(len(result_a[u'ins+dels']), 0)

        self.assertEqual(len(result_b[u'ins']), 0)
        self.assertEqual(len(result_b[u'dels']), 0)
        self.assertEqual(len(result_b[u'subs']), 1)
        self.assertEqual(len(result_b[u'ins+dels']), 0)

    def test_suggestions(self):
        """
        Test the suggestions function.
        """
        orig = u'aaaa'
        s0 = u'aaaa'  # match
        s1 = u'baaa'  # edit distance 1
        s1a = u'caaa'  # edit distance 1; after s1 by alphabetical order
        s2 = u'aabb'  # edit distance 2
        s2a = u'aacc'  # edit distance 2; after s2 by alphabetical order
        s3 = u'cccc'  # edit distance 4
        s4 = u'ccccc'  # edit distance 5
        # s4 inserted twice to increase frequency
        expected = [s0, s1, s1a, s2, s2a, s3, s4, s4]
        self.assertEqual(expected, algorithms.suggestions(
            orig, [s4, s4, s2, s2a, s0, s1, s1a, s3]))

if __name__ == '__main__':
    unittest.main()
