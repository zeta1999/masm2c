from __future__ import absolute_import
from __future__ import print_function

from tasm import parser
from tasm import cpp
from tasm import op
from tasm import proc
from tasm import lex

from builtins import chr
from builtins import hex
from builtins import object
from builtins import range
from builtins import str
import future.types
from future.types import Integral
import future.types.newobject
from future.types.newobject import newobject
import future.types.newrange
from future.types.newrange import newrange
import future.types.newstr
from future.types.newstr import BaseNewStr
from future.types.newstr import newstr
import logging
from logging import BufferingFormatter
from mock import patch
import ntpath
import re
from re import Scanner
import re, string, os
import sys
import tasm.lex
import tasm.op
from tasm.op import label
from tasm.op import var
import tasm.parser
from tasm.parser import Parser
import tasm.proc
from tasm.proc import Proc
import traceback
import unittest

class ParserTest(unittest.TestCase):

    def test_convert_data_to_blob(self):
        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u"'00000000'", u'0Dh', u'0Ah', u"'$'"]),[48, 48, 48, 48, 48, 48, 48, 48, 13, 10, 36])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u"'Hello World From Protected Mode!'", u'10', u'13', u"'$'"]),[72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 32, 70, 114, 111, 109, 32, 80, 114, 111, 116, 101, 99, 116, 101, 100, 32, 77, 111, 100, 101, 33, 10, 13, 36])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u"'OKOKOKOK'", u'10', u'13']),[79, 75, 79, 75, 79, 75, 79, 75, 10, 13])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u"'OKOKOKOK'"]),[79, 75, 79, 75, 79, 75, 79, 75])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u"'ab''cd'"]),[97, 98, 39, 39, 99, 100])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u"'file.txt'", u'0']),[102, 105, 108, 101, 46, 116, 120, 116, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'1']),[1])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'10 dup (?)']),[0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'100 dup (1)']),[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'12']),[12])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'131']),[131])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'141']),[141])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'2', u'5', u'6']),[2, 5, 6])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'2']),[2])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'4 dup (5)']),[5, 5, 5, 5])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'4']),[4])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'5 dup (0)']),[0, 0, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'5*5 dup (0', u'testEqu*2', u'2*2', u'3)']),[0, 0, 4, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'6']),[6])

        self.assertEqual(parser_instance.convert_data_to_blob(width=2,data=[u'11']),[11, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=2,data=[u'2', u'5', u'0']),[2, 0, 5, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=2,data=[u'2']),[2, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=2,data=[u'223', u'22']),[223, 0, 22, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=2,data=[u'4', u'6', u'9']),[4, 0, 6, 0, 9, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'0']),[0, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'10 dup (?)']),[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'11', u'-11', u'2', u'4']),[11, 0, 0, 0, 245, 255, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'11', u'-11', u'2', u'4000000']),[11, 0, 0, 0, 245, 255, 0, 0, 2, 0, 0, 0, 0, 9, 61, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'111', u'1']),[111, 0, 0, 0, 1, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'3']),[3, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'34']),[34, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'9', u'8', u'7', u'1']),[9, 0, 0, 0, 8, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'offset var5']),[0, 0, 0, 0])
        self.assertEqual(parser_instance.convert_data_to_blob(width=4,data=[u'test2']),[0, 0, 0, 0])
        #self.assertEqual(parser_instance.convert_data_to_blob(width=1,data=[u'2*2 dup (0,testEqu*2,2*2,3)']),[0, 0, 0, 0])
    '''

    '''
    @patch.object(logging, 'debug')
    @patch.object(logging, 'warning')
    def test_convert_data_to_c(self, mock_warning, mock_debug):
        mock_warning.return_value = None
        mock_debug.return_value = None
        parser_instance = Parser([])

        #self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'offset var5'],label=''),(['', 'offset(_data,var5)', ', // dummy1\n'], ['dw dummy1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u"'00000000'", u'0Dh', u'0Ah', u"'$'"],label=u'ASCII'),(['{', u"'0','0','0','0','0','0','0','0','\\r','\\n','$'", '}', u', // ASCII\n'], ['char ASCII[11]', ';\n'], 2))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u"'Hello World From Protected Mode!'", u'10', u'13', u"'$'"],label=u'_msg'),(['{', u"'H','e','l','l','o',' ','W','o','r','l','d',' ','F','r','o','m',' ','P','r','o','t','e','c','t','e','d',' ','M','o','d','e','!','\\n','\\r','$'", '}', u', // _msg\n'], ['char _msg[35]', ';\n'], 2))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u"'OKOKOKOK'", u'10', u'13'],label=''),(['{', u"'O','K','O','K','O','K','O','K','\\n','\\r'", '}', ', // dummy1\n'], ['char dummy1[10]', ';\n'], 2))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u"'OKOKOKOK'"],label=''),(['{', u"'O','K','O','K','O','K','O','K'", '}', ', // dummy1\n'], ['char dummy1[8]', ';\n'], 0))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u"'ab''cd'"],label=u'doublequote'),(['{', u"'a','b','\\'','\\'','c','d'", '}', u', // doublequote\n'], ['char doublequote[6]', ';\n'], 0))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u"'file.txt'", u'0'],label=u'fileName'),(['', u'"file.txt"', u', // fileName\n'], ['char fileName[9]', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'1'],label=u'var1'),(['', '1', u', // var1\n'], [u'db var1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'10 dup (?)'],label=u'var0'),(['{', '0,', '0,', '0,', '0,', '0,', '0,', '0,', '0,', '0,', '0', '}', u', // var0\n'], ['db var0[10]', ';\n'], 10))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'100 dup (1)'],label=u'var4'),(['{', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1,', '1', '}', u', // var4\n'], ['db var4[100]', ';\n'], 100))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'12'],label=''),(['', '12', ', // dummy1\n'], ['db dummy1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'131'],label=u'var4'),(['', '131', u', // var4\n'], [u'db var4', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'141'],label=''),(['', '141', ', // dummy1\n'], ['db dummy1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'2', u'5', u'6'],label=u'var1'),(['{', '2,', '5,', '6', '}', u', // var1\n'], ['db var1[3]', ';\n'], 3))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'2'],label=u'var1'),(['', '2', u', // var1\n'], [u'db var1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'4 dup (5)'],label=''),(['{', '5,', '5,', '5,', '5', '}', ', // dummy1\n'], ['db dummy1[4]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'4 dup (5)'],label=u'var'),(['{', '5,', '5,', '5,', '5', '}', u', // var\n'], ['db var[4]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'4'],label=u'beginningdata'),(['', '4', u', // beginningdata\n'], [u'db beginningdata', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'4'],label=u'enddata'),(['', '4', u', // enddata\n'], [u'db enddata', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'5 dup (0)'],label=u'var2'),(['{', '0,', '0,', '0,', '0,', '0', '}', u', // var2\n'], ['db var2[5]', ';\n'], 5))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'5*5 dup (0', u'testEqu*2', u'2*2', u'3)'],label=u'var3'),(['{', '0,', '0,', '4,', '0', '}', ', // var3\n'], ['db var3[4]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'6'],label=u'var1'),(['', '6', u', // var1\n'], [u'db var1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=2,data=[u'11'],label=u'var2'),(['', '11', u', // var2\n'], [u'dw var2', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=2,data=[u'2', u'5', u'0'],label=u'var5'),(['{', '2,', '5,', '0', '}', u', // var5\n'], ['dw var5[3]', ';\n'], 3))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=2,data=[u'2'],label=u'var2'),(['', '2', u', // var2\n'], [u'dw var2', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=2,data=[u'223', u'22'],label=''),(['{', '223,', '22', '}', ', // dummy1\n'], ['dw dummy1[2]', ';\n'], 2))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=2,data=[u'4', u'6', u'9'],label=u'var2'),(['{', '4,', '6,', '9', '}', u', // var2\n'], ['dw var2[3]', ';\n'], 3))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'0'],label=u'load_handle'),(['', '0', u', // load_handle\n'], [u'dd load_handle', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'10 dup (?)'],label=u'var5'),(['{', '0,', '0,', '0,', '0,', '0,', '0,', '0,', '0,', '0,', '0', '}', u', // var5\n'], ['dd var5[10]', ';\n'], 10))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'11', u'-11', u'2', u'4'],label=u'var3'),(['{', '11,', '4294967285,', '2,', '4', '}', u', // var3\n'], ['dd var3[4]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'11', u'-11', u'2', u'4000000'],label=u'var3'),(['{', '11,', '4294967285,', '2,', '4000000', '}', u', // var3\n'], ['dd var3[4]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'111', u'1'],label=''),(['{', '111,', '1', '}', ', // dummy1\n'], ['dd dummy1[2]', ';\n'], 2))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'3'],label=u'var3'),(['', '3', u', // var3\n'], [u'dd var3', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'34'],label=u'var3'),(['', '34', u', // var3\n'], [u'dd var3', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'9', u'8', u'7', u'1'],label=u'var6'),(['{', '9,', '8,', '7,', '1', '}', u', // var6\n'], ['dd var6[4]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'offset var5'],label=''),(['', '0', ', // dummy1\n'], ['dw dummy1', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=4,data=[u'test2'],label=u'var3'),(['', '0', u', // var3\n'], [u'dd var3', ';\n'], 1))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,data=["'abcde\0\0'"],label=u'var5'),(['{', "'a','b','c','d','e','\\0','\\0'", '}', ', // var5\n'], ['char var5[7]', ';\n'], 0))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,label='_a_mod_nst_669_s',data=["'.MOD.'", '0', '0', '0', '0']),(['', '".MOD.\\0\\0\\0"', ', // _a_mod_nst_669_s\n'], ['char _a_mod_nst_669_s[9]', ';\n'], 4))

        parser_instance = Parser([])
        self.assertEqual(parser_instance.convert_data_to_c(width=1,label=u'var3',data=["'*'", '10', '11', '3 * 15 DUP(0)']),(['', '"*\\n\\x0b"', ', // var3\n'], ['char var3[4]', ';\n'], 3))

        #parser_instance = Parser([])
        #self.assertEqual(parser_instance.convert_data_to_c(width=1,data=[u'2*2 dup (0,testEqu*2,2*2,3)']),[0, 0, 0, 0])

    @patch.object(logging, 'debug')
    @patch.object(logging, 'info')
    #@patch.object(parser, 'get_global')
    def test_convert_data(self, mock_info, mock_debug):
        #mock_get_global.return_value = var()
        mock_info.return_value = None
        mock_debug.return_value = None
        parser_instance = Parser([])

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=256, v=u'2*2')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=256, v=u'3)')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=256, v=u'5*5 dup (0')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=256, v=u'testEqu*2')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=4294967296, v=u'test2')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=65536, v=u'2*2')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=65536, v=u'3)')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=65536, v=u'5*5 dup (0')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=65536, v=u'test2')

        with self.assertRaises(KeyError):
            parser_instance.get_global_value(base=65536, v=u'testEqu*2')

        #self.assertEqual(parser_instance.convert_data(base=4294967296,v=u'var5'),u'offset(_data,var5)')

    @patch.object(logging, 'debug')
    def test_fix_dollar(self, mock_debug):
        mock_debug.return_value = None
        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='3'),'3')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='1'),'1')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='-13'),'-13')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='13'),'13')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='4'),'4')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='var1'),'var1')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='1'),'1')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='2'),'2')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='(00+38*3)*320+1/2+33*(3-1)'),'(00+38*3)*320+1/2+33*(3-1)')

        parser_instance = Parser([])
        self.assertEqual(parser_instance.fix_dollar(v='1500 ; 8*2*3 ;+1 +19*13*2*4'),'1500 ; 8*2*3 ;+1 +19*13*2*4')

    def test_parse_int(self):
        parser_instance = Parser([])

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u"'Z' - 'A' +1")
        
        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u"'a'")

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u"'c'")

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u"'d'")

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u"'tseT'")

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'3)')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'5*5 dup (0')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'B')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'CC')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'DDD')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'OFFSET ASCiI')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'OFFSET AsCii')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[doublequote+4]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[edi+1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[edi]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[load_handle]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var+3]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var+4]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var-1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var0+5]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var1+1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var2+2]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var2-1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var2]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var3+3*4]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var3+ebp]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var3]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'[var]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'_data')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'al')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'beginningdata')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'bl')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'buffer')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'bx')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'byte ptr [edi+1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'byte ptr [edi+7]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'byte ptr dl')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'cl')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'cx')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'dl')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'ds')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'ds:[edi]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'dword ptr buffer')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'dx')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'eax')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'ebp')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'ebx')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'ecx')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'edi')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'edx')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'enddata')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'es')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'esi')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'fileName')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'offset _msg')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'offset var1')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'offset var2')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'offset var5')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'teST2')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'test2')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'testEqu*2')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var1')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var1[1]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var1[bx+si]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var1[bx]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var2')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var3')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var3+3*4')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'var3+ebp')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'word ptr [var5+2]')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'word ptr var5')

        with self.assertRaises(ValueError):
            parser_instance.parse_int(v=u'ah')

        self.assertEqual(parser_instance.parse_int(v=u'14*320'),4480)
        self.assertEqual(parser_instance.parse_int(v=u'2*2'),4)
        self.assertEqual(parser_instance.parse_int(v=u'3*4'),12)
        self.assertEqual(parser_instance.parse_int(v=u'-1-(-2+3)'),-2)
        self.assertEqual(parser_instance.parse_int(v=u'-1'),-1)
        self.assertEqual(parser_instance.parse_int(v=u'-11'),-11)
        self.assertEqual(parser_instance.parse_int(v=u'-2'),-2)
        self.assertEqual(parser_instance.parse_int(v=u'0'),0)
        self.assertEqual(parser_instance.parse_int(v=u'00h'),0)
        self.assertEqual(parser_instance.parse_int(v=u'03dh'),61)
        self.assertEqual(parser_instance.parse_int(v=u'03eh'),62)
        self.assertEqual(parser_instance.parse_int(v=u'03fh'),63)
        self.assertEqual(parser_instance.parse_int(v=u'042h'),66)
        self.assertEqual(parser_instance.parse_int(v=u'0Ah'),10)
        self.assertEqual(parser_instance.parse_int(v=u'0Dh'),13)
        self.assertEqual(parser_instance.parse_int(v=u'0Fh'),15)
        self.assertEqual(parser_instance.parse_int(v=u'0ffffff00h'),4294967040)
        self.assertEqual(parser_instance.parse_int(v=u'1'),1)
        self.assertEqual(parser_instance.parse_int(v=u'10'),10)
        self.assertEqual(parser_instance.parse_int(v=u'100'),100)
        self.assertEqual(parser_instance.parse_int(v=u'1000h'),4096)
        self.assertEqual(parser_instance.parse_int(v=u'11'),11)
        self.assertEqual(parser_instance.parse_int(v=u'111'),111)
        self.assertEqual(parser_instance.parse_int(v=u'12'),12)
        self.assertEqual(parser_instance.parse_int(v=u'13'),13)
        self.assertEqual(parser_instance.parse_int(v=u'131'),131)
        self.assertEqual(parser_instance.parse_int(v=u'16'),16)
        self.assertEqual(parser_instance.parse_int(v=u'2'),2)
        self.assertEqual(parser_instance.parse_int(v=u'21h'),33)
        self.assertEqual(parser_instance.parse_int(v=u'22'),22)
        self.assertEqual(parser_instance.parse_int(v=u'223'),223)
        self.assertEqual(parser_instance.parse_int(v=u'25'),25)
        self.assertEqual(parser_instance.parse_int(v=u'3'),3)
        self.assertEqual(parser_instance.parse_int(v=u'30h'),48)
        self.assertEqual(parser_instance.parse_int(v=u'34'),34)
        self.assertEqual(parser_instance.parse_int(v=u'35'),35)
        self.assertEqual(parser_instance.parse_int(v=u'37'),37)
        self.assertEqual(parser_instance.parse_int(v=u'39h'),57)
        self.assertEqual(parser_instance.parse_int(v=u'4'),4)
        self.assertEqual(parser_instance.parse_int(v=u'4000000'),4000000)
        self.assertEqual(parser_instance.parse_int(v=u'4ch'),76)
        self.assertEqual(parser_instance.parse_int(v=u'5'),5)
        self.assertEqual(parser_instance.parse_int(v=u'50'),50)
        self.assertEqual(parser_instance.parse_int(v=u'6'),6)
        self.assertEqual(parser_instance.parse_int(v=u'64000'),64000)
        self.assertEqual(parser_instance.parse_int(v=u'7'),7)
        self.assertEqual(parser_instance.parse_int(v=u'0h'),0)
        self.assertEqual(parser_instance.parse_int(v=u'0b'),0)

    def test_calculate_data_size(self):
        parser_instance = Parser([])
        self.assertEqual(parser_instance.calculate_data_size(cmd0='b'),1)
        self.assertEqual(parser_instance.calculate_data_size(cmd0='d'),4)
        self.assertEqual(parser_instance.calculate_data_size(cmd0='q'),8)
        self.assertEqual(parser_instance.calculate_data_size(cmd0='w'),2)
        self.assertEqual(parser_instance.calculate_data_size(cmd0='t'),10)
        
    @patch.object(logging, 'debug')
    def test_action_data(self, mock_debug):
        mock_debug.return_value = None
        parser_instance = Parser([])

        self.assertEqual(parser_instance.action_data(line="ASCII DB '00000000',0Dh,0Ah,'$' ; buffer for ASCII string"),("{'0','0','0','0','0','0','0','0','\\r','\\n','$'}, // ascii\n",'char ascii[11];\n',11))
        self.assertEqual(parser_instance.action_data(line="_a070295122642\tdb '07/02/95 12:26:42',0 ; DATA XREF: seg003:off_2462E\x19o"),('"07/02/95 12:26:42", // _a070295122642\n','char _a070295122642[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_a100Assembler\tdb '100% assembler!'"),("{'1','0','0','%',' ','a','s','s','e','m','b','l','e','r','!'}, // _a100assembler\n",'char _a100assembler[15];\n',15))
        self.assertEqual(parser_instance.action_data(line="_a1024\t\tdb '1024',0"),('"1024", // _a1024\n','char _a1024[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="_a130295211558\tdb '13/02/95 21:15:58',0 ; DATA XREF: _read_module+BE\x18w"),('"13/02/95 21:15:58", // _a130295211558\n','char _a130295211558[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_a1Thru0		db '1 Thru 0'"),("{'1',' ','T','h','r','u',' ','0'}, // _a1thru0\n",'char _a1thru0[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_a2284116_8	db '2:284/116.8'"),("{'2',':','2','8','4','/','1','1','6','.','8'}, // _a2284116_8\n",'char _a2284116_8[11];\n', 11))
        self.assertEqual(parser_instance.action_data(line="_a24bitInterpolation db ' 24bit Interpolation'"),("{' ','2','4','b','i','t',' ','I','n','t','e','r','p','o','l','a','t','i','o','n'}, // _a24bitinterpolation\n",'char _a24bitinterpolation[20];\n', 20))
        self.assertEqual(parser_instance.action_data(line="_a256		db '256',0              ; DATA XREF: _text_init2+1CEo"),('"256", // _a256\n','char _a256[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_a512		db '512',0"),('"512", // _a512\n','char _a512[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_a768		db '768',0"),('"768", // _a768\n','char _a768[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aAdlibSoundcard	db 'Adlib SoundCard',0  ; DATA XREF: dseg:02BAo"),('"Adlib SoundCard", // _aadlibsoundcard\n','char _aadlibsoundcard[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aAdlibSoundcard_0 db 'Adlib SoundCard',0 ; DATA XREF: seg003:0D6Ao"),('"Adlib SoundCard", // _aadlibsoundcard_0\n','char _aadlibsoundcard_0[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aAnd		db ' and '"),("{' ','a','n','d',' '}, // _aand\n",'char _aand[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="_aAndWriteFollowingTe db	' and write following text in your message:'"),("{' ','a','n','d',' ','w','r','i','t','e',' ','f','o','l','l','o','w','i','n','g',' ','t','e','x','t',' ','i','n',' ','y','o','u','r',' ','m','e','s','s','a','g','e',':'}, // _aandwritefollowingte\n",'char _aandwritefollowingte[42];\n', 42))
        self.assertEqual(parser_instance.action_data(line="_aArpeggio	db 'Arpeggio       ',0  ; DATA XREF: seg001:loc_1AB0Do"),('"Arpeggio       ", // _aarpeggio\n','char _aarpeggio[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aAt		db ' at',0              ; DATA XREF: seg003:10BFo seg003:1152o ..."),('" at", // _aat\n','char _aat[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aAutoToneporta	db 'Auto TonePorta ',0"),('"Auto TonePorta ", // _aautotoneporta\n','char _aautotoneporta[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aBackspace	db 'BackSpace'"),("{'B','a','c','k','S','p','a','c','e'}, // _abackspace\n",'char _abackspace[9];\n', 9))
        self.assertEqual(parser_instance.action_data(line="_aBasePort	db ' base port ',0      ; DATA XREF: seg003:10C3o seg003:1156o ..."),('" base port ", // _abaseport\n','char _abaseport[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aBmod2stm	db 'BMOD2STM'"),("{'B','M','O','D','2','S','T','M'}, // _abmod2stm\n",'char _abmod2stm[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_aCd81		db 'CD81'"),("{'C','D','8','1'}, // _acd81\n",'char _acd81[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aCh		db 'CH'"),("{'C','H'}, // _ach\n",'char _ach[2];\n', 2))
        self.assertEqual(parser_instance.action_data(line="_aChannels	db 'Channels      :'"),("{'C','h','a','n','n','e','l','s',' ',' ',' ',' ',' ',' ',':'}, // _achannels\n",'char _achannels[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aChn		db 'CHN'"),("{'C','H','N'}, // _achn\n",'char _achn[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aConfigFileNotF	db 'Config file not found. Run ISETUP first',0Dh,0Ah,'$'"),("{'C','o','n','f','i','g',' ','f','i','l','e',' ','n','o','t',' ','f','o','u','n','d','.',' ','R','u','n',' ','I','S','E','T','U','P',' ','f','i','r','s','t','\\r','\\n','$'}, // _aconfigfilenotf\n",'char _aconfigfilenotf[42];\n', 42))
        self.assertEqual(parser_instance.action_data(line="_aCopyrightC1994	db 'Copyright (c) 1994,1995 by Stefan Danes and Ramon van Gorkom',0"),('"Copyright (c) 1994,1995 by Stefan Danes and Ramon van Gorkom", // _acopyrightc1994\n','char _acopyrightc1994[61];\n', 61))
        self.assertEqual(parser_instance.action_data(line="_aCouldNotFindT_0 db 'Could not find the Gravis UltraSound at the specified port addres'"),("{'C','o','u','l','d',' ','n','o','t',' ','f','i','n','d',' ','t','h','e',' ','G','r','a','v','i','s',' ','U','l','t','r','a','S','o','u','n','d',' ','a','t',' ','t','h','e',' ','s','p','e','c','i','f','i','e','d',' ','p','o','r','t',' ','a','d','d','r','e','s'}, // _acouldnotfindt_0\n",'char _acouldnotfindt_0[65];\n', 65))
        self.assertEqual(parser_instance.action_data(line="_aCouldNotFindThe db 'Could not find the ULTRASND environment string',0Dh,0Ah,0"),('"Could not find the ULTRASND environment string\\r\\n", // _acouldnotfindthe\n','char _acouldnotfindthe[49];\n', 49))
        self.assertEqual(parser_instance.action_data(line="_aCovox		db 'Covox',0            ; DATA XREF: dseg:02B6o"),('"Covox", // _acovox\n','char _acovox[6];\n', 6))
        self.assertEqual(parser_instance.action_data(line="_aCovox_0	db 'Covox',0            ; DATA XREF: seg003:0D66o"),('"Covox", // _acovox_0\n','char _acovox_0[6];\n', 6))
        self.assertEqual(parser_instance.action_data(line="_aCriticalErrorT	db 0Dh,0Ah		; DATA XREF: _start+31o"),('{13,10}, // _acriticalerrort\n','db _acriticalerrort[2];\n', 2))
        self.assertEqual(parser_instance.action_data(line="_aCtrlDel	db 'Ctrl Del'"),("{'C','t','r','l',' ','D','e','l'}, // _actrldel\n",'char _actrldel[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_aCurrentSoundcard db 0Dh,'Current Soundcard settings:',0Dh,0Ah ; DATA XREF: _start:loc_19057o"),("{'\\r','C','u','r','r','e','n','t',' ','S','o','u','n','d','c','a','r','d',' ','s','e','t','t','i','n','g','s',':','\\r','\\n'}, // _acurrentsoundcard\n",'char _acurrentsoundcard[30];\n', 30))
        self.assertEqual(parser_instance.action_data(line="_aCurrentTrack	db 'Current Track :'"),("{'C','u','r','r','e','n','t',' ','T','r','a','c','k',' ',':'}, // _acurrenttrack\n",'char _acurrenttrack[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aCursor		db 7Fh"),('127, // _acursor\n','db _acursor;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aCursor_0	db 'Cursor ',1Bh,' '"),("{'C','u','r','s','o','r',' ',27,' '}, // _acursor_0\n",'char _acursor_0[9];\n', 9))
        self.assertEqual(parser_instance.action_data(line="_aCursor_1	db 'Cursor '"),("{'C','u','r','s','o','r',' '}, // _acursor_1\n",'char _acursor_1[7];\n', 7))
        self.assertEqual(parser_instance.action_data(line="_aDecIncAmplify	db 7Eh"),('126, // _adecincamplify\n','db _adecincamplify;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aDecIncAmplify_0 db '  Dec/Inc amplify'"),("{' ',' ','D','e','c','/','I','n','c',' ','a','m','p','l','i','f','y'}, // _adecincamplify_0\n",'char _adecincamplify_0[17];\n', 17))
        self.assertEqual(parser_instance.action_data(line="_aDecIncVolume	db 7Eh"),('126, // _adecincvolume\n','db _adecincvolume;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aDecIncVolume_0	db '  Dec/Inc volume'"),("{' ',' ','D','e','c','/','I','n','c',' ','v','o','l','u','m','e'}, // _adecincvolume_0\n",'char _adecincvolume_0[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aDel		db 'Del'"),("{'D','e','l'}, // _adel\n",'char _adel[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aDeleteAllFilesWhich db	'Delete all files which are marked to delete'"),("{'D','e','l','e','t','e',' ','a','l','l',' ','f','i','l','e','s',' ','w','h','i','c','h',' ','a','r','e',' ','m','a','r','k','e','d',' ','t','o',' ','d','e','l','e','t','e'}, // _adeleteallfileswhich\n",'char _adeleteallfileswhich[43];\n', 43))
        self.assertEqual(parser_instance.action_data(line="_aDeleteMarkedFil db 'Delete marked files? [Y/N]',0 ; DATA XREF: _start+635o"),('"Delete marked files? [Y/N]", // _adeletemarkedfil\n','char _adeletemarkedfil[27];\n', 27))
        self.assertEqual(parser_instance.action_data(line="_aDeletingFile	db 'Deleting file: '    ; DATA XREF: _start+69Fo"),("{'D','e','l','e','t','i','n','g',' ','f','i','l','e',':',' '}, // _adeletingfile\n",'char _adeletingfile[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aDeviceNotIniti	db 'Device not initialised!',0 ; DATA XREF: sub_12D05+8o"),('"Device not initialised!", // _adevicenotiniti\n','char _adevicenotiniti[24];\n', 24))
        self.assertEqual(parser_instance.action_data(line="_aDisableBpmOnOf	db 7Eh"),('126, // _adisablebpmonof\n','db _adisablebpmonof;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aDisableBpmOnOff db ' Disable BPM on/off'"),("{' ','D','i','s','a','b','l','e',' ','B','P','M',' ','o','n','/','o','f','f'}, // _adisablebpmonoff\n",'char _adisablebpmonoff[19];\n', 19))
        self.assertEqual(parser_instance.action_data(line="_aDma		db ', DMA '"),("{',',' ','D','M','A',' '}, // _adma\n",'char _adma[6];\n', 6))
        self.assertEqual(parser_instance.action_data(line="_aDosShellTypeEx	db 7Eh"),('126, // _adosshelltypeex\n','db _adosshelltypeex;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aDosShellTypeExitT_0 db	'DOS Shell (Type EXIT to return)'"),("{'D','O','S',' ','S','h','e','l','l',' ','(','T','y','p','e',' ','E','X','I','T',' ','t','o',' ','r','e','t','u','r','n',')'}, // _adosshelltypeexitt_0\n",'char _adosshelltypeexitt_0[31];\n', 31))
        self.assertEqual(parser_instance.action_data(line="_aDosShellTypeExitToR db	'  DOS Shell (Type EXIT to return)'"),("{' ',' ','D','O','S',' ','S','h','e','l','l',' ','(','T','y','p','e',' ','E','X','I','T',' ','t','o',' ','r','e','t','u','r','n',')'}, // _adosshelltypeexittor\n",'char _adosshelltypeexittor[33];\n', 33))
        self.assertEqual(parser_instance.action_data(line="_aDramDma	db ', DRAM-DMA '"),("{',',' ','D','R','A','M','-','D','M','A',' '}, // _adramdma\n",'char _adramdma[11];\n', 11))
        self.assertEqual(parser_instance.action_data(line="_aE_command	db 'E_Command      ',0"),('"E_Command      ", // _ae_command\n','char _ae_command[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aE_g_		db 'E.G.'"),("{'E','.','G','.'}, // _ae_g_\n",'char _ae_g_[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aEnd		db 'End'"),("{'E','n','d'}, // _aend\n",'char _aend[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aEndPattern	db '  End pattern'"),("{' ',' ','E','n','d',' ','p','a','t','t','e','r','n'}, // _aendpattern\n",'char _aendpattern[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_aEnd_0		db 'End'"),("{'E','n','d'}, // _aend_0\n",'char _aend_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aEnter		db 'Enter'"),("{'E','n','t','e','r'}, // _aenter\n",'char _aenter[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="_aErrorCouldNotFi db 'Error: Could not find IRQ/DMA!',0Dh,0Ah,0"),('"Error: Could not find IRQ/DMA!\\r\\n", // _aerrorcouldnotfi\n','char _aerrorcouldnotfi[33];\n', 33))
        self.assertEqual(parser_instance.action_data(line="_aErrorCouldNot_0 db 'Error: Could not find IRQ!',0Dh,0Ah,0 ; DATA XREF: _sb_detect_irq+4Co"),('"Error: Could not find IRQ!\\r\\n", // _aerrorcouldnot_0\n','char _aerrorcouldnot_0[29];\n', 29))
        self.assertEqual(parser_instance.action_data(line="_aErrorCouldNot_1 db 'Error: Could not find DMA!',0Dh,0Ah,0 ; DATA XREF: _sb_detect_irq+D6o"),('"Error: Could not find DMA!\\r\\n", // _aerrorcouldnot_1\n','char _aerrorcouldnot_1[29];\n', 29))
        self.assertEqual(parser_instance.action_data(line="_aErrorSoundcardN db 'Error: Soundcard not found!',0Dh,0Ah,'$',0"),('"Error: Soundcard not found!\\r\\n$", // _aerrorsoundcardn\n','char _aerrorsoundcardn[31];\n', 31))
        self.assertEqual(parser_instance.action_data(line="_aEsc		db 'ESC'"),("{'E','S','C'}, // _aesc\n",'char _aesc[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aExit		db 'EXIT'"),("{'E','X','I','T'}, // _aexit\n",'char _aexit[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF1		db 'F-1'"),("{'F','-','1'}, // _af1\n",'char _af1[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF10		db 7Fh"),('127, // _af10\n','db _af10;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aF10_0		db 'F-10'"),("{'F','-','1','0'}, // _af10_0\n",'char _af10_0[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF10_1		db 'F-10'"),("{'F','-','1','0'}, // _af10_1\n",'char _af10_1[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF11		db 7Fh"),('127, // _af11\n','db _af11;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aF11_0		db 'F-11'"),("{'F','-','1','1'}, // _af11_0\n",'char _af11_0[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF11_1		db 'F-11'"),("{'F','-','1','1'}, // _af11_1\n",'char _af11_1[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF12		db 7Fh"),('127, // _af12\n','db _af12;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aF12_0		db 'F-12'"),("{'F','-','1','2'}, // _af12_0\n",'char _af12_0[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF12_1		db 'F-12'"),("{'F','-','1','2'}, // _af12_1\n",'char _af12_1[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aF2_0		db 'F-2'"),("{'F','-','2'}, // _af2_0\n",'char _af2_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF3_0		db 'F-3'"),("{'F','-','3'}, // _af3_0\n",'char _af3_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF4_0		db 'F-4'"),("{'F','-','4'}, // _af4_0\n",'char _af4_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF5_0		db 'F-5'"),("{'F','-','5'}, // _af5_0\n",'char _af5_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF8_0		db 'F-8'"),("{'F','-','8'}, // _af8_0\n",'char _af8_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF8_1		db 'F-8'"),("{'F','-','8'}, // _af8_1\n",'char _af8_1[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF9		db ' [F-9]              ',0"),('" [F-9]              ", // _af9\n','char _af9[21];\n', 21))
        self.assertEqual(parser_instance.action_data(line="_aF9_0		db ' [F-9]',0"),('" [F-9]", // _af9_0\n','char _af9_0[7];\n', 7))
        self.assertEqual(parser_instance.action_data(line="_aF9_1		db 7Fh"),('127, // _af9_1\n','db _af9_1;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aF9_2		db 'F-9'"),("{'F','-','9'}, // _af9_2\n",'char _af9_2[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF9_3		db 'F-9'"),("{'F','-','9'}, // _af9_3\n",'char _af9_3[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aF9_4		db 'F-9'"),("{'F','-','9'}, // _af9_4\n",'char _af9_4[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aFar		db 'FAR■'"),("{'F','A','R','\\xfe'}, // _afar\n",'char _afar[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aFarFineTempo	db 'FAR Fine Tempo ',0"),('"FAR Fine Tempo ", // _afarfinetempo\n','char _afarfinetempo[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFarTempo	db 'FAR Tempo      ',0"),('"FAR Tempo      ", // _afartempo\n','char _afartempo[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFastErForward	db '  Fast(er) forward'"),("{' ',' ','F','a','s','t','(','e','r',')',' ','f','o','r','w','a','r','d'}, // _afasterforward\n",'char _afasterforward[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aFastErRewind	db '  Fast(er) rewind'"),("{' ',' ','F','a','s','t','(','e','r',')',' ','r','e','w','i','n','d'}, // _afasterrewind\n",'char _afasterrewind[17];\n', 17))
        self.assertEqual(parser_instance.action_data(line="_aFastfourierFrequenc db	'  FastFourier Frequency Analysis'"),("{' ',' ','F','a','s','t','F','o','u','r','i','e','r',' ','F','r','e','q','u','e','n','c','y',' ','A','n','a','l','y','s','i','s'}, // _afastfourierfrequenc\n",'char _afastfourierfrequenc[32];\n', 32))
        self.assertEqual(parser_instance.action_data(line="_aFidonet	db 'FidoNet  : '"),("{'F','i','d','o','N','e','t',' ',' ',':',' '}, // _afidonet\n",'char _afidonet[11];\n', 11))
        self.assertEqual(parser_instance.action_data(line="_aFile		db 'File'               ; DATA XREF: _start+689w _start+6A8o"),("{'F','i','l','e'}, // _afile\n",'char _afile[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aFileSelectorHelp db 'File Selector Help'"),("{'F','i','l','e',' ','S','e','l','e','c','t','o','r',' ','H','e','l','p'}, // _afileselectorhelp\n",'char _afileselectorhelp[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aFilename_0	db 'Filename      : '"),("{'F','i','l','e','n','a','m','e',' ',' ',' ',' ',' ',' ',':',' '}, // _afilename_0\n",'char _afilename_0[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFilename_ext	db 'FileName.Ext'       ; DATA XREF: _read_module:loc_19E41o"),("{'F','i','l','e','N','a','m','e','.','E','x','t'}, // _afilename_ext\n",'char _afilename_ext[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aFinePanning	db 'Fine Panning   ',0"),('"Fine Panning   ", // _afinepanning\n','char _afinepanning[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFinePortVolsl	db 'Fine Port+VolSl',0"),('"Fine Port+VolSl", // _afineportvolsl\n','char _afineportvolsl[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFinePortaDown	db 'Fine Porta Down',0"),('"Fine Porta Down", // _afineportadown\n','char _afineportadown[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFinePortaUp	db 'Fine Porta Up  ',0"),('"Fine Porta Up  ", // _afineportaup\n','char _afineportaup[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFineTonePorta	db 'Fine Tone Porta',0"),('"Fine Tone Porta", // _afinetoneporta\n','char _afinetoneporta[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFineVibrVolsl	db 'Fine Vibr+VolSl',0"),('"Fine Vibr+VolSl", // _afinevibrvolsl\n','char _afinevibrvolsl[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFineVibrato	db 'Fine Vibrato   ',0"),('"Fine Vibrato   ", // _afinevibrato\n','char _afinevibrato[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFineVolSlide	db 'Fine Vol Slide ',0"),('"Fine Vol Slide ", // _afinevolslide\n','char _afinevolslide[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFineslideDown	db 'FineSlide Down ',0"),('"FineSlide Down ", // _afineslidedown\n','char _afineslidedown[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFineslideUp	db 'FineSlide Up   ',0"),('"FineSlide Up   ", // _afineslideup\n','char _afineslideup[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFinevolumeDown	db 'FineVolume Down',0"),('"FineVolume Down", // _afinevolumedown\n','char _afinevolumedown[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFinevolumeUp	db 'FineVolume Up  ',0"),('"FineVolume Up  ", // _afinevolumeup\n','char _afinevolumeup[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aFlt4		db 'FLT4'"),("{'F','L','T','4'}, // _aflt4\n",'char _aflt4[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aFlt8		db 'FLT8'"),("{'F','L','T','8'}, // _aflt8\n",'char _aflt8[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aGeneralMidi	db 'General MIDI',0     ; DATA XREF: dseg:02BEo"),('"General MIDI", // _ageneralmidi\n','char _ageneralmidi[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_aGeneralMidi_0	db 'General MIDI',0     ; DATA XREF: seg003:0D6Eo"),('"General MIDI", // _ageneralmidi_0\n','char _ageneralmidi_0[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_aGlissandoCtrl	db 'Glissando Ctrl ',0"),('"Glissando Ctrl ", // _aglissandoctrl\n','char _aglissandoctrl[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aGraphicalScopesOneF db	'  Graphical scopes, one for each channel'"),("{' ',' ','G','r','a','p','h','i','c','a','l',' ','s','c','o','p','e','s',',',' ','o','n','e',' ','f','o','r',' ','e','a','c','h',' ','c','h','a','n','n','e','l'}, // _agraphicalscopesonef\n",'char _agraphicalscopesonef[40];\n', 40))
        self.assertEqual(parser_instance.action_data(line="_aGravisMaxCodec	db 'Gravis MAX Codec',0"),('"Gravis MAX Codec", // _agravismaxcodec\n','char _agravismaxcodec[17];\n', 17))
        self.assertEqual(parser_instance.action_data(line="_aGravisUltrasou	db 'Gravis UltraSound',0 ; DATA XREF: dseg:_table_sndcrdnameo"),('"Gravis UltraSound", // _agravisultrasou\n','char _agravisultrasou[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aGravisUltrasoun db 'Gravis UltraSound',0 ; DATA XREF: seg003:_snd_cards_offso"),('"Gravis UltraSound", // _agravisultrasoun\n','char _agravisultrasoun[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aGray		db 7Fh"),('127, // _agray\n','db _agray;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aGray_0		db 'Gray - +'"),("{'G','r','a','y',' ','-',' ','+'}, // _agray_0\n",'char _agray_0[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_aGsft		db 'GSFT'"),("{'G','S','F','T'}, // _agsft\n",'char _agsft[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aGuess___	db '  Guess...'"),("{' ',' ','G','u','e','s','s','.','.','.'}, // _aguess___\n",'char _aguess___[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_aHGf1Irq	db 'h, GF1-IRQ '"),("{'h',',',' ','G','F','1','-','I','R','Q',' '}, // _ahgf1irq\n",'char _ahgf1irq[11];\n', 11))
        self.assertEqual(parser_instance.action_data(line="_aHIrq		db 'h, IRQ '"),("{'h',',',' ','I','R','Q',' '}, // _ahirq\n",'char _ahirq[7];\n', 7))
        self.assertEqual(parser_instance.action_data(line="_aHitBackspaceToRe db 'Hit backspace to return to playmode, F-1 for help, QuickRead='"),("{'H','i','t',' ','b','a','c','k','s','p','a','c','e',' ','t','o',' ','r','e','t','u','r','n',' ','t','o',' ','p','l','a','y','m','o','d','e',',',' ','F','-','1',' ','f','o','r',' ','h','e','l','p',',',' ','Q','u','i','c','k','R','e','a','d','='}, // _ahitbackspacetore\n",'char _ahitbackspacetore[61];\n', 61))
        self.assertEqual(parser_instance.action_data(line="_aHome		db 'Home'"),("{'H','o','m','e'}, // _ahome\n",'char _ahome[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aHopeYouLikedUsingTh db	'Hope you liked using the '"),("{'H','o','p','e',' ','y','o','u',' ','l','i','k','e','d',' ','u','s','i','n','g',' ','t','h','e',' '}, // _ahopeyoulikedusingth\n",'char _ahopeyoulikedusingth[25];\n', 25))
        self.assertEqual(parser_instance.action_data(line="_aIf		db 'if'"),("{'i','f'}, // _aif\n",'char _aif[2];\n', 2))
        self.assertEqual(parser_instance.action_data(line="_aIfYouHaveBugReports db	'If you have bug-reports, suggestions or comments send a message t'"),("{'I','f',' ','y','o','u',' ','h','a','v','e',' ','b','u','g','-','r','e','p','o','r','t','s',',',' ','s','u','g','g','e','s','t','i','o','n','s',' ','o','r',' ','c','o','m','m','e','n','t','s',' ','s','e','n','d',' ','a',' ','m','e','s','s','a','g','e',' ','t'}, // _aifyouhavebugreports\n",'char _aifyouhavebugreports[65];\n', 65))
        self.assertEqual(parser_instance.action_data(line="_aIgnoreBpmChanges db ' Ignore BPM changes'"),("{' ','I','g','n','o','r','e',' ','B','P','M',' ','c','h','a','n','g','e','s'}, // _aignorebpmchanges\n",'char _aignorebpmchanges[19];\n', 19))
        self.assertEqual(parser_instance.action_data(line="_aInertiaMailinglists db	'Inertia Mailinglists'"),("{'I','n','e','r','t','i','a',' ','M','a','i','l','i','n','g','l','i','s','t','s'}, // _ainertiamailinglists\n",'char _ainertiamailinglists[20];\n', 20))
        self.assertEqual(parser_instance.action_data(line="_aInertiaModule	db 'Inertia Module: ',0 ; DATA XREF: _useless_writeinr+29o"),('"Inertia Module: ", // _ainertiamodule\n','char _ainertiamodule[17];\n', 17))
        self.assertEqual(parser_instance.action_data(line="_aInertiaModule_0 db 'Inertia Module: ',0 ; DATA XREF: _useless_writeinr+23o"),('"Inertia Module: ", // _ainertiamodule_0\n','char _ainertiamodule_0[17];\n', 17))
        self.assertEqual(parser_instance.action_data(line="_aInertiaModule_1 db 'Inertia Module: '"),("{'I','n','e','r','t','i','a',' ','M','o','d','u','l','e',':',' '}, // _ainertiamodule_1\n",'char _ainertiamodule_1[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aInertiaPlayer	db 'Inertia Player'"),("{'I','n','e','r','t','i','a',' ','P','l','a','y','e','r'}, // _ainertiaplayer\n",'char _ainertiaplayer[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aInertiaPlayerV1_ db 'Inertia Player V1.22 written by Stefan Danes and Ramon van Gorkom'"),("{'I','n','e','r','t','i','a',' ','P','l','a','y','e','r',' ','V','1','.','2','2',' ','w','r','i','t','t','e','n',' ','b','y',' ','S','t','e','f','a','n',' ','D','a','n','e','s',' ','a','n','d',' ','R','a','m','o','n',' ','v','a','n',' ','G','o','r','k','o','m'}, // _ainertiaplayerv1_\n",'char _ainertiaplayerv1_[65];\n', 65))
        self.assertEqual(parser_instance.action_data(line="_aInertiaPlayerV1_22A db	'Inertia Player V1.22 Assembly ',27h,'94 CD Edition by Sound Solution'"),("{'I','n','e','r','t','i','a',' ','P','l','a','y','e','r',' ','V','1','.','2','2',' ','A','s','s','e','m','b','l','y',' ',39,'9','4',' ','C','D',' ','E','d','i','t','i','o','n',' ','b','y',' ','S','o','u','n','d',' ','S','o','l','u','t','i','o','n'}, // _ainertiaplayerv1_22a\n",'char _ainertiaplayerv1_22a[62];\n', 62))
        self.assertEqual(parser_instance.action_data(line="_aInertiaPlayer_0 db 'Inertia Player',0"),('"Inertia Player", // _ainertiaplayer_0\n','char _ainertiaplayer_0[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aInertiaSample	db 'Inertia Sample: '   ; DATA XREF: _useless_writeinr_118+11o"),("{'I','n','e','r','t','i','a',' ','S','a','m','p','l','e',':',' '}, // _ainertiasample\n",'char _ainertiasample[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aInternet	db 'Internet : '"),("{'I','n','t','e','r','n','e','t',' ',':',' '}, // _ainternet\n",'char _ainternet[11];\n', 11))
        self.assertEqual(parser_instance.action_data(line="_aInvertLoop	db 'Invert Loop    ',0"),('"Invert Loop    ", // _ainvertloop\n','char _ainvertloop[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aJanfebmaraprmayj db '   JanFebMarAprMayJunJulAugSepOctNovDec'"),("{' ',' ',' ','J','a','n','F','e','b','M','a','r','A','p','r','M','a','y','J','u','n','J','u','l','A','u','g','S','e','p','O','c','t','N','o','v','D','e','c'}, // _ajanfebmaraprmayj\n",'char _ajanfebmaraprmayj[39];\n', 39))
        self.assertEqual(parser_instance.action_data(line="_aJn		db 'JN'"),("{'J','N'}, // _ajn\n",'char _ajn[2];\n', 2))
        self.assertEqual(parser_instance.action_data(line="_aJumpToLoop	db 'Jump To Loop   ',0"),('"Jump To Loop   ", // _ajumptoloop\n','char _ajumptoloop[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aKb		db 'KB',0               ; DATA XREF: _text_init2+1D7o"),('"KB", // _akb\n','char _akb[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aKhz		db 'kHz',0              ; DATA XREF: seg003:117Bo seg003:11ADo ..."),('"kHz", // _akhz\n','char _akhz[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aListFileNotFou	db 'List file not found.',0Dh,0Ah,'$' ; DATA XREF: _start+D07o"),("{'L','i','s','t',' ','f','i','l','e',' ','n','o','t',' ','f','o','u','n','d','.','\\r','\\n','$'}, // _alistfilenotfou\n",'char _alistfilenotfou[23];\n', 23))
        self.assertEqual(parser_instance.action_data(line="_aListserver@oliver_s db	'listserver@oliver.sun.ac.za'"),("{'l','i','s','t','s','e','r','v','e','r','@','o','l','i','v','e','r','.','s','u','n','.','a','c','.','z','a'}, // _alistserverarboliver_s\n",'char _alistserverarboliver_s[27];\n', 27))
        self.assertEqual(parser_instance.action_data(line="_aLoadingModule	db 'Loading module',0   ; DATA XREF: _start+41Ao"),('"Loading module", // _aloadingmodule\n','char _aloadingmodule[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aLoopModule	db 7Eh"),('126, // _aloopmodule\n','db _aloopmodule;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aLoopModuleWhenDone db ' Loop Module when done'"),("{' ','L','o','o','p',' ','M','o','d','u','l','e',' ','w','h','e','n',' ','d','o','n','e'}, // _aloopmodulewhendone\n",'char _aloopmodulewhendone[22];\n', 22))
        self.assertEqual(parser_instance.action_data(line="_aLoopModule_0	db ' Loop module'"),("{' ','L','o','o','p',' ','m','o','d','u','l','e'}, // _aloopmodule_0\n",'char _aloopmodule_0[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aLoopPattern	db '  Loop pattern'"),("{' ',' ','L','o','o','p',' ','p','a','t','t','e','r','n'}, // _alooppattern\n",'char _alooppattern[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aMK		db 'M&K!'"),("{'M','&','K','!'}, // _amk\n",'char _amk[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aMK_0		db 'M!K!'"),("{'M','!','K','!'}, // _amk_0\n",'char _amk_0[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aM_k_		db 'M.K.'"),("{'M','.','K','.'}, // _am_k_\n",'char _am_k_[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aMainVolume	db 'Main Volume   :'"),("{'M','a','i','n',' ','V','o','l','u','m','e',' ',' ',' ',':'}, // _amainvolume\n",'char _amainvolume[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aMarkFileToDelete db 'Mark file to delete'"),("{'M','a','r','k',' ','f','i','l','e',' ','t','o',' ','d','e','l','e','t','e'}, // _amarkfiletodelete\n",'char _amarkfiletodelete[19];\n', 19))
        self.assertEqual(parser_instance.action_data(line="_aMarkedToDelete	db '<Marked to Delete>    ',0 ; DATA XREF: _filelist_198B8+10Do"),('"<Marked to Delete>    ", // _amarkedtodelete\n','char _amarkedtodelete[23];\n', 23))
        self.assertEqual(parser_instance.action_data(line="_aMas_utrack_v	db 'MAS_UTrack_V'"),("{'M','A','S','_','U','T','r','a','c','k','_','V'}, // _amas_utrack_v\n",'char _amas_utrack_v[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aMixedAt	db ', mixed at ',0      ; DATA XREF: seg003:1173o seg003:11A5o ..."),('", mixed at ", // _amixedat\n','char _amixedat[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aModuleIsCorrupt db 'Module is corrupt!',0 ; DATA XREF: _start+439o"),('"Module is corrupt!", // _amoduleiscorrupt\n','char _amoduleiscorrupt[19];\n', 19))
        self.assertEqual(parser_instance.action_data(line="_aModuleLoadErro	db 'Module load error.',0Dh,0Ah,'$' ; DATA XREF: _readallmoules+1Bo"),("{'M','o','d','u','l','e',' ','l','o','a','d',' ','e','r','r','o','r','.','\\r','\\n','$'}, // _amoduleloaderro\n",'char _amoduleloaderro[21];\n', 21))
        self.assertEqual(parser_instance.action_data(line="_aModuleNotFound	db 'Module not found.',0Dh,0Ah,'$' ; DATA XREF: _find_mods+88o"),("{'M','o','d','u','l','e',' ','n','o','t',' ','f','o','u','n','d','.','\\r','\\n','$'}, // _amodulenotfound\n",'char _amodulenotfound[20];\n', 20))
        self.assertEqual(parser_instance.action_data(line="_aModuleType_0	db 'Module Type   : '"),("{'M','o','d','u','l','e',' ','T','y','p','e',' ',' ',' ',':',' '}, // _amoduletype_0\n",'char _amoduletype_0[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aMtm		db 'MTM'"),("{'M','T','M'}, // _amtm\n",'char _amtm[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aMute		db '<Mute>                ',0 ; DATA XREF: seg001:1949o"),('"<Mute>                ", // _amute\n','char _amute[23];\n', 23))
        self.assertEqual(parser_instance.action_data(line="_aMuteChannel	db '  Mute channel'"),("{' ',' ','M','u','t','e',' ','c','h','a','n','n','e','l'}, // _amutechannel\n",'char _amutechannel[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aName		db 'name'               ; DATA XREF: _start+692w"),("{'n','a','m','e'}, // _aname\n",'char _aname[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aNotEnoughDramOn db 'Not enough DRAM on UltraSound',0Dh,0Ah,0"),('"Not enough DRAM on UltraSound\\r\\n", // _anotenoughdramon\n','char _anotenoughdramon[32];\n', 32))
        self.assertEqual(parser_instance.action_data(line="_aNotEnoughDram_0 db 'Not enough DRAM on your UltraSound to load all samples!',0"),('"Not enough DRAM on your UltraSound to load all samples!", // _anotenoughdram_0\n','char _anotenoughdram_0[56];\n', 56))
        self.assertEqual(parser_instance.action_data(line="_aNotEnoughMemo_0 db 'Not enough memory available to load all samples!',0"),('"Not enough memory available to load all samples!", // _anotenoughmemo_0\n','char _anotenoughmemo_0[49];\n', 49))
        self.assertEqual(parser_instance.action_data(line="_aNotEnoughMemor	db 'Not enough memory.',0Dh,0Ah,'$' ; DATA XREF: _start+23Do"),("{'N','o','t',' ','e','n','o','u','g','h',' ','m','e','m','o','r','y','.','\\r','\\n','$'}, // _anotenoughmemor\n",'char _anotenoughmemor[21];\n', 21))
        self.assertEqual(parser_instance.action_data(line="_aNotEnoughMemory db 'Not enough Memory available',0Dh,0Ah,0"),('"Not enough Memory available\\r\\n", // _anotenoughmemory\n','char _anotenoughmemory[30];\n', 30))
        self.assertEqual(parser_instance.action_data(line="_aNoteCut	db 'Note Cut       ',0"),('"Note Cut       ", // _anotecut\n','char _anotecut[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aNoteDelay	db 'Note Delay     ',0"),('"Note Delay     ", // _anotedelay\n','char _anotedelay[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aNtsc		db '(NTSC)',0           ; DATA XREF: _txt_draw_bottom+53o"),('"(NTSC)", // _antsc\n','char _antsc[7];\n', 7))
        self.assertEqual(parser_instance.action_data(line="_aOcta		db 'OCTA'"),("{'O','C','T','A'}, // _aocta\n",'char _aocta[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aPal		db '(PAL) ',0           ; DATA XREF: _txt_draw_bottom+49o"),('"(PAL) ", // _apal\n','char _apal[7];\n', 7))
        self.assertEqual(parser_instance.action_data(line="_aPatternBreak	db 'Pattern Break  ',0"),('"Pattern Break  ", // _apatternbreak\n','char _apatternbreak[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aPatternDelay	db 'Pattern Delay  ',0"),('"Pattern Delay  ", // _apatterndelay\n','char _apatterndelay[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aPause		db 'Pause'"),("{'P','a','u','s','e'}, // _apause\n",'char _apause[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="_aPcHonker	db 'PC Honker',0        ; DATA XREF: dseg:02BCo"),('"PC Honker", // _apchonker\n','char _apchonker[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_aPcHonker_0	db 'PC Honker',0        ; DATA XREF: seg003:0D6Co"),('"PC Honker", // _apchonker_0\n','char _apchonker_0[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_aPgdn		db 'PgDn'"),("{'P','g','D','n'}, // _apgdn\n",'char _apgdn[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aPgup		db 'PgUp'"),("{'P','g','U','p'}, // _apgup\n",'char _apgup[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aPlayer13029521	db 'Player: '"),("{'P','l','a','y','e','r',':',' '}, // _aplayer13029521\n",'char _aplayer13029521[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_aPlayingInStereoFree db	' Playing in Stereo, Free:'"),("{' ','P','l','a','y','i','n','g',' ','i','n',' ','S','t','e','r','e','o',',',' ','F','r','e','e',':'}, // _aplayinginstereofree\n",'char _aplayinginstereofree[25];\n', 25))
        self.assertEqual(parser_instance.action_data(line="_aPlaypausloop	db 'PlayPausLoop'       ; DATA XREF: _txt_draw_bottom+164o"),("{'P','l','a','y','P','a','u','s','L','o','o','p'}, // _aplaypausloop\n",'char _aplaypausloop[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aPortVolslide	db 'Port + VolSlide',0"),('"Port + VolSlide", // _aportvolslide\n','char _aportvolslide[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aPortamentoDown	db 'Portamento Down',0"),('"Portamento Down", // _aportamentodown\n','char _aportamentodown[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aPortamentoUp	db 'Portamento Up  ',0"),('"Portamento Up  ", // _aportamentoup\n','char _aportamentoup[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aPositionJump	db 'Position Jump  ',0"),('"Position Jump  ", // _apositionjump\n','char _apositionjump[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aPress		db 'Press '"),("{'P','r','e','s','s',' '}, // _apress\n",'char _apress[6];\n', 6))
        self.assertEqual(parser_instance.action_data(line="_aPressAnyKeyToReturn db	'Press any key to return to the fileselector',0"),('"Press any key to return to the fileselector", // _apressanykeytoreturn\n','char _apressanykeytoreturn[44];\n', 44))
        self.assertEqual(parser_instance.action_data(line="_aPressF1ForHelpQu db '                 Press F-1 for help, QuickRead='"),("{' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','P','r','e','s','s',' ','F','-','1',' ','f','o','r',' ','h','e','l','p',',',' ','Q','u','i','c','k','R','e','a','d','='}, // _apressf1forhelpqu\n",'char _apressf1forhelpqu[47];\n', 47))
        self.assertEqual(parser_instance.action_data(line="_aProAudioSpectr	db 'Pro Audio Spectrum 16',0 ; DATA XREF: dseg:02ACo"),('"Pro Audio Spectrum 16", // _aproaudiospectr\n','char _aproaudiospectr[22];\n', 22))
        self.assertEqual(parser_instance.action_data(line="_aProAudioSpectrum db 'Pro Audio Spectrum 16',0 ; DATA XREF: seg003:0D5Co"),('"Pro Audio Spectrum 16", // _aproaudiospectrum\n','char _aproaudiospectrum[22];\n', 22))
        self.assertEqual(parser_instance.action_data(line="_aProtracker1_0C	db 7Eh"),('126, // _aprotracker1_0c\n','db _aprotracker1_0c;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aProtracker1_0Compat db	'  ProTracker 1.0 compatibility on/off'"),("{' ',' ','P','r','o','T','r','a','c','k','e','r',' ','1','.','0',' ','c','o','m','p','a','t','i','b','i','l','i','t','y',' ','o','n','/','o','f','f'}, // _aprotracker1_0compat\n",'char _aprotracker1_0compat[37];\n', 37))
        self.assertEqual(parser_instance.action_data(line="_aProtracker1_0_0 db ' ProTracker 1.0'"),("{' ','P','r','o','T','r','a','c','k','e','r',' ','1','.','0'}, // _aprotracker1_0_0\n",'char _aprotracker1_0_0[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aPsm		db 'PSM■'"),("{'P','S','M','\\xfe'}, // _apsm\n",'char _apsm[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aQuitIplay	db 'Quit IPLAY'"),("{'Q','u','i','t',' ','I','P','L','A','Y'}, // _aquitiplay\n",'char _aquitiplay[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_aRealtimeVuMeters db '  Realtime VU meters'"),("{' ',' ','R','e','a','l','t','i','m','e',' ','V','U',' ','m','e','t','e','r','s'}, // _arealtimevumeters\n",'char _arealtimevumeters[20];\n', 20))
        self.assertEqual(parser_instance.action_data(line="_aRetrigVolume	db 'Retrig+Volume  ',0"),('"Retrig+Volume  ", // _aretrigvolume\n','char _aretrigvolume[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aRetriggerNote	db 'Retrigger Note ',0"),('"Retrigger Note ", // _aretriggernote\n','char _aretriggernote[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aReturnToPlaymodeOnl db	'Return to playmode [Only if the music is playing]'"),("{'R','e','t','u','r','n',' ','t','o',' ','p','l','a','y','m','o','d','e',' ','[','O','n','l','y',' ','i','f',' ','t','h','e',' ','m','u','s','i','c',' ','i','s',' ','p','l','a','y','i','n','g',']'}, // _areturntoplaymodeonl\n",'char _areturntoplaymodeonl[49];\n', 49))
        self.assertEqual(parser_instance.action_data(line="_aSamplename	db '# SampleName   '    ; DATA XREF: seg001:1B7Co"),("{'#',' ','S','a','m','p','l','e','N','a','m','e',' ',' ',' '}, // _asamplename\n",'char _asamplename[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aSamplesUsed	db 'Samples Used  :'"),("{'S','a','m','p','l','e','s',' ','U','s','e','d',' ',' ',':'}, // _asamplesused\n",'char _asamplesused[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aScream		db '!Scream!'"),("{'!','S','c','r','e','a','m','!'}, // _ascream\n",'char _ascream[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_aScrm		db 'SCRM'"),("{'S','C','R','M'}, // _ascrm\n",'char _ascrm[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aScrolllock	db 'ScrollLock'"),("{'S','c','r','o','l','l','L','o','c','k'}, // _ascrolllock\n",'char _ascrolllock[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_aSdanes@marvels_hack db	'sdanes@marvels.hacktic.nl'"),("{'s','d','a','n','e','s','@','m','a','r','v','e','l','s','.','h','a','c','k','t','i','c','.','n','l'}, // _asdanesarbmarvels_hack\n",'char _asdanesarbmarvels_hack[25];\n', 25))
        self.assertEqual(parser_instance.action_data(line="_aSendEmailTo	db 'Send email to '"),("{'S','e','n','d',' ','e','m','a','i','l',' ','t','o',' '}, // _asendemailto\n",'char _asendemailto[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aSetAmplify	db 'Set Amplify    ',0"),('"Set Amplify    ", // _asetamplify\n','char _asetamplify[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetFilter	db 'Set Filter     ',0  ; DATA XREF: seg001:1A9Ao"),('"Set Filter     ", // _asetfilter\n','char _asetfilter[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetFinetune	db 'Set FineTune   ',0"),('"Set FineTune   ", // _asetfinetune\n','char _asetfinetune[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetLoopPoint	db 'Set Loop Point ',0  ; DATA XREF: seg001:1A8Fo"),('"Set Loop Point ", // _asetlooppoint\n','char _asetlooppoint[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetPanning	db 'Set Panning    ',0"),('"Set Panning    ", // _asetpanning\n','char _asetpanning[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetSampleOfs	db 'Set Sample Ofs ',0"),('"Set Sample Ofs ", // _asetsampleofs\n','char _asetsampleofs[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetSpeed	db 'Set Speed      ',0"),('"Set Speed      ", // _asetspeed\n','char _asetspeed[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetSpeedBpm	db 'Set Speed/BPM  ',0"),('"Set Speed/BPM  ", // _asetspeedbpm\n','char _asetspeedbpm[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aSetStmSpeed	db 'Set STM Speed  ',0"),('"Set STM Speed  ", // _asetstmspeed\n','char _asetstmspeed[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aShell130295211	db 'Shell: 13/02/95 21:15:58'"),("{'S','h','e','l','l',':',' ','1','3','/','0','2','/','9','5',' ','2','1',':','1','5',':','5','8'}, // _ashell130295211\n",'char _ashell130295211[24];\n', 24))
        self.assertEqual(parser_instance.action_data(line="_aShellingToOperating db	'Shelling to Operating System...'"),("{'S','h','e','l','l','i','n','g',' ','t','o',' ','O','p','e','r','a','t','i','n','g',' ','S','y','s','t','e','m','.','.','.'}, // _ashellingtooperating\n",'char _ashellingtooperating[31];\n', 31))
        self.assertEqual(parser_instance.action_data(line="_aSizeVolModeC2T	db '~   Size Vol Mode  C-2 Tune LoopPos LoopEnd',0"),('"~   Size Vol Mode  C-2 Tune LoopPos LoopEnd", // _asizevolmodec2t\n','char _asizevolmodec2t[44];\n', 44))
        self.assertEqual(parser_instance.action_data(line="_aSoYouWantedSomeHelp db	'So you wanted some help?'"),("{'S','o',' ','y','o','u',' ','w','a','n','t','e','d',' ','s','o','m','e',' ','h','e','l','p','?'}, // _asoyouwantedsomehelp\n",'char _asoyouwantedsomehelp[24];\n', 24))
        self.assertEqual(parser_instance.action_data(line="_aSomeFunctionsOf db 'Some functions of the UltraSound do not work!',0Dh,0Ah"),("{'S','o','m','e',' ','f','u','n','c','t','i','o','n','s',' ','o','f',' ','t','h','e',' ','U','l','t','r','a','S','o','u','n','d',' ','d','o',' ','n','o','t',' ','w','o','r','k','!','\\r','\\n'}, // _asomefunctionsof\n",'char _asomefunctionsof[47];\n', 47))
        self.assertEqual(parser_instance.action_data(line="_aSoundBlaster	db 'Sound Blaster',0    ; DATA XREF: dseg:02B4o"),('"Sound Blaster", // _asoundblaster\n','char _asoundblaster[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aSoundBlaster16	db 'Sound Blaster 16/16ASP',0 ; DATA XREF: dseg:02B0o"),('"Sound Blaster 16/16ASP", // _asoundblaster16\n','char _asoundblaster16[23];\n', 23))
        self.assertEqual(parser_instance.action_data(line="_aSoundBlaster1616 db 'Sound Blaster 16/16ASP',0 ; DATA XREF: seg003:0D60o"),('"Sound Blaster 16/16ASP", // _asoundblaster1616\n','char _asoundblaster1616[23];\n', 23))
        self.assertEqual(parser_instance.action_data(line="_aSoundBlasterPr	db 'Sound Blaster Pro',0 ; DATA XREF: dseg:02B2o"),('"Sound Blaster Pro", // _asoundblasterpr\n','char _asoundblasterpr[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aSoundBlasterPro db 'Sound Blaster Pro',0 ; DATA XREF: seg003:0D62o"),('"Sound Blaster Pro", // _asoundblasterpro\n','char _asoundblasterpro[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aSoundBlaster_0	db 'Sound Blaster',0    ; DATA XREF: seg003:0D64o"),('"Sound Blaster", // _asoundblaster_0\n','char _asoundblaster_0[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aSpeed		db 'Speed'"),("{'S','p','e','e','d'}, // _aspeed\n",'char _aspeed[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="_aStereoOn1	db 'Stereo-On-1',0      ; DATA XREF: dseg:02B8o"),('"Stereo-On-1", // _astereoon1\n','char _astereoon1[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aStereoOn1_0	db 'Stereo-On-1',0      ; DATA XREF: seg003:0D68o"),('"Stereo-On-1", // _astereoon1_0\n','char _astereoon1_0[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_aSubscribeInertiaLis db	'subscribe inertia-list YourRealName'"),("{'s','u','b','s','c','r','i','b','e',' ','i','n','e','r','t','i','a','-','l','i','s','t',' ','Y','o','u','r','R','e','a','l','N','a','m','e'}, // _asubscribeinertialis\n",'char _asubscribeinertialis[35];\n', 35))
        self.assertEqual(parser_instance.action_data(line="_aSubscribeInertiaTal db	'subscribe inertia-talk YourRealName',0"),('"subscribe inertia-talk YourRealName", // _asubscribeinertiatal\n','char _asubscribeinertiatal[36];\n', 36))
        self.assertEqual(parser_instance.action_data(line="_aTab		db 'Tab'"),("{'T','a','b'}, // _atab\n",'char _atab[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aTab_0		db 'Tab'"),("{'T','a','b'}, // _atab_0\n",'char _atab_0[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aTdz		db 'TDZ'"),("{'T','D','Z'}, // _atdz\n",'char _atdz[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_aThe		db 'the '"),("{'t','h','e',' '}, // _athe\n",'char _athe[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aThisHelpScreenButIG db	'This help screen, but I guess you already found it...'"),("{'T','h','i','s',' ','h','e','l','p',' ','s','c','r','e','e','n',',',' ','b','u','t',' ','I',' ','g','u','e','s','s',' ','y','o','u',' ','a','l','r','e','a','d','y',' ','f','o','u','n','d',' ','i','t','.','.','.'}, // _athishelpscreenbutig\n",'char _athishelpscreenbutig[53];\n', 53))
        self.assertEqual(parser_instance.action_data(line="_aThisProgramRequ db 'This program requires the soundcards device driver.',0Dh,0Ah,0"),('"This program requires the soundcards device driver.\\r\\n", // _athisprogramrequ\n','char _athisprogramrequ[54];\n', 54))
        self.assertEqual(parser_instance.action_data(line="_aToConnectToBinaryIn db	'To connect to Binary Inertia releases: '"),("{'T','o',' ','c','o','n','n','e','c','t',' ','t','o',' ','B','i','n','a','r','y',' ','I','n','e','r','t','i','a',' ','r','e','l','e','a','s','e','s',':',' '}, // _atoconnecttobinaryin\n",'char _atoconnecttobinaryin[39];\n', 39))
        self.assertEqual(parser_instance.action_data(line="_aToConnectToDiscussi db	'To connect to Discussion Mailing list: '"),("{'T','o',' ','c','o','n','n','e','c','t',' ','t','o',' ','D','i','s','c','u','s','s','i','o','n',' ','M','a','i','l','i','n','g',' ','l','i','s','t',':',' '}, // _atoconnecttodiscussi\n",'char _atoconnecttodiscussi[39];\n', 39))
        self.assertEqual(parser_instance.action_data(line="_aToMoveTheHighlighte db	' to move the highlighted bar'"),("{' ','t','o',' ','m','o','v','e',' ','t','h','e',' ','h','i','g','h','l','i','g','h','t','e','d',' ','b','a','r'}, // _atomovethehighlighte\n",'char _atomovethehighlighte[28];\n', 28))
        self.assertEqual(parser_instance.action_data(line="_aToPlayTheModuleOrSe db	' to play the module or select the drive/directory'"),("{' ','t','o',' ','p','l','a','y',' ','t','h','e',' ','m','o','d','u','l','e',' ','o','r',' ','s','e','l','e','c','t',' ','t','h','e',' ','d','r','i','v','e','/','d','i','r','e','c','t','o','r','y'}, // _atoplaythemoduleorse\n",'char _atoplaythemoduleorse[49];\n', 49))
        self.assertEqual(parser_instance.action_data(line="_aToReturnTo	db ' to return to '"),("{' ','t','o',' ','r','e','t','u','r','n',' ','t','o',' '}, // _atoreturnto\n",'char _atoreturnto[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_aToSubscribeToOneOrB db	' to subscribe to one or both of'"),("{' ','t','o',' ','s','u','b','s','c','r','i','b','e',' ','t','o',' ','o','n','e',' ','o','r',' ','b','o','t','h',' ','o','f'}, // _atosubscribetooneorb\n",'char _atosubscribetooneorb[31];\n', 31))
        self.assertEqual(parser_instance.action_data(line="_aToggle24bitInt	db 7Eh"),('126, // _atoggle24bitint\n','db _atoggle24bitint;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_aToggle24bitInterpol db	' Toggle 24bit Interpolation'"),("{' ','T','o','g','g','l','e',' ','2','4','b','i','t',' ','I','n','t','e','r','p','o','l','a','t','i','o','n'}, // _atoggle24bitinterpol\n",'char _atoggle24bitinterpol[27];\n', 27))
        self.assertEqual(parser_instance.action_data(line="_aTogglePalNtsc	db '  Toggle PAL/NTSC',0"),('"  Toggle PAL/NTSC", // _atogglepalntsc\n','char _atogglepalntsc[18];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_aToggleQuickreadingO db	'Toggle QuickReading of module name'"),("{'T','o','g','g','l','e',' ','Q','u','i','c','k','R','e','a','d','i','n','g',' ','o','f',' ','m','o','d','u','l','e',' ','n','a','m','e'}, // _atogglequickreadingo\n",'char _atogglequickreadingo[34];\n', 34))
        self.assertEqual(parser_instance.action_data(line="_aTonePortamento	db 'Tone Portamento',0"),('"Tone Portamento", // _atoneportamento\n','char _atoneportamento[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aTrackPosition	db 'Track Position:'"),("{'T','r','a','c','k',' ','P','o','s','i','t','i','o','n',':'}, // _atrackposition\n",'char _atrackposition[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aTremolo	db 'Tremolo        ',0"),('"Tremolo        ", // _atremolo\n','char _atremolo[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aTremoloControl	db 'Tremolo Control',0"),('"Tremolo Control", // _atremolocontrol\n','char _atremolocontrol[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aTremor		db 'Tremor         ',0"),('"Tremor         ", // _atremor\n','char _atremor[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aTriller	db 'Triller        ',0"),('"Triller        ", // _atriller\n','char _atriller[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aType		db 'Type '"),("{'T','y','p','e',' '}, // _atype\n",'char _atype[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="_aUnused256	db ' Unused'"),("{'\x7f',' ','U','n','u','s','e','d'}, // _aunused256\n",'char _aunused256[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="_aUse		db 'Use '"),("{'U','s','e',' '}, // _ause\n",'char _ause[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_aVibrVolslide	db 'Vibr + VolSlide',0"),('"Vibr + VolSlide", // _avibrvolslide\n','char _avibrvolslide[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aVibrato	db 'Vibrato        ',0"),('"Vibrato        ", // _avibrato\n','char _avibrato[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aVibratoControl	db 'Vibrato Control',0"),('"Vibrato Control", // _avibratocontrol\n','char _avibratocontrol[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aViewSampleNamesTwic db	'  View sample names (twice for more)'"),("{' ',' ','V','i','e','w',' ','s','a','m','p','l','e',' ','n','a','m','e','s',' ','(','t','w','i','c','e',' ','f','o','r',' ','m','o','r','e',')'}, // _aviewsamplenamestwic\n",'char _aviewsamplenamestwic[36];\n', 36))
        self.assertEqual(parser_instance.action_data(line="_aVolumeAmplify	db 'Volume Amplify:'"),("{'V','o','l','u','m','e',' ','A','m','p','l','i','f','y',':'}, // _avolumeamplify\n",'char _avolumeamplify[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_aVolumeChange	db 'Volume Change  ',0"),('"Volume Change  ", // _avolumechange\n','char _avolumechange[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aVolumeSliding	db 'Volume Sliding ',0"),('"Volume Sliding ", // _avolumesliding\n','char _avolumesliding[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_aWhichIsWrittenIn db ' which is written in '"),("{' ','w','h','i','c','h',' ','i','s',' ','w','r','i','t','t','e','n',' ','i','n',' '}, // _awhichiswrittenin\n",'char _awhichiswrittenin[21];\n', 21))
        self.assertEqual(parser_instance.action_data(line="_aWindowsSoundSy	db 'Windows Sound System',0 ; DATA XREF: dseg:02AEo"),('"Windows Sound System", // _awindowssoundsy\n','char _awindowssoundsy[21];\n', 21))
        self.assertEqual(parser_instance.action_data(line="_aWindowsSoundSyst db 'Windows Sound System',0 ; DATA XREF: seg003:0D5Eo"),('"Windows Sound System", // _awindowssoundsyst\n','char _awindowssoundsyst[21];\n', 21))
        self.assertEqual(parser_instance.action_data(line="_aXpressF4ForMor	db 'xPress F-4 for more'"),("{'x','P','r','e','s','s',' ','F','-','4',' ','f','o','r',' ','m','o','r','e'}, // _axpressf4formor\n",'char _axpressf4formor[19];\n', 19))
        self.assertEqual(parser_instance.action_data(line="_a_ext		db '.Ext'               ; DATA XREF: _start+69Bw"),("{'.','E','x','t'}, // _a_ext\n",'char _a_ext[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_a_m_k		db '.M.K'"),("{'.','M','.','K'}, // _a_m_k\n",'char _a_m_k[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_a_mod_nst_669_s	db '.MOD.NST.669.STM.S3M.MTM.PSM.WOW.INR.FAR.ULT.OKT.OCT',0,0,0,0"),('".MOD.NST.669.STM.S3M.MTM.PSM.WOW.INR.FAR.ULT.OKT.OCT\\0\\0\\0", // _a_mod_nst_669_s\n','char _a_mod_nst_669_s[56];\n', 56))
        self.assertEqual(parser_instance.action_data(line="_amount_of_x	dw 0			; DATA XREF: _read_module+75w"),('0, // _amount_of_x\n','dw _amount_of_x;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_amplification	dw 100			; DATA XREF: _clean_11C43+83w"),('100, // _amplification\n','dw _amplification;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_asmprintf_tbl	dw offset _mysprintf_0_nop ; DATA XREF: _myasmsprintf+1Cr"),('0, // _asmprintf_tbl\n','dw _asmprintf_tbl;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_atop_title	dw 152h			; DATA XREF: _txt_draw_top_title+12o"),('338, // _atop_title\n','dw _atop_title;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_base_port2	dw 0			; DATA XREF: _wss_init:loc_147C3w"),('0, // _base_port2\n','dw _base_port2;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_bit_mode	db 8			; DATA XREF: sub_12DA8+55w"),('8, // _bit_mode\n','db _bit_mode;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_bottom_menu	dw 0Ah			; DATA XREF: _text_init2+21Fo"),('10, // _bottom_menu\n','dw _bottom_menu;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_buffer_1DBEC	db 0			; DATA XREF: _find_mods+32o"),('0, // _buffer_1dbec\n','db _buffer_1dbec;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_buffer_1DC6C	dd 0			; DATA XREF: _start+2C5w _start+2D3o ..."),('0, // _buffer_1dc6c\n','dd _buffer_1dc6c;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_buffer_1seg	dw 0			; DATA XREF: _text_init2+18Bw"),('0, // _buffer_1seg\n','dw _buffer_1seg;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_buffer_2seg	dw 0			; DATA XREF: seg001:loc_1A913w"),('0, // _buffer_2seg\n','dw _buffer_2seg;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_byte_11C29	db 0			; DATA XREF: sub_11C0C:loc_11C14r"),('0, // _byte_11c29\n','db _byte_11c29;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_13C54	db 0,9,12h,1Bh,24h,2Dh,36h,40h,40h,4Ah,53h,5Ch,65h,6Eh"),('{0,9,18,27,36,45,54,64,64,74,83,92,101,110}, // _byte_13c54\n','db _byte_13c54[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_byte_14F70	db 0			; DATA XREF: _configure_timer+12w"),('0, // _byte_14f70\n','db _byte_14f70;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_14F71	db 0			; DATA XREF: sub_12D35:loc_12D41w"),('0, // _byte_14f71\n','db _byte_14f71;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_14F72	db 0			; DATA XREF: sub_13CF6+Dw _text:4F51r"),('0, // _byte_14f72\n','db _byte_14f72;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_14F73	db 0			; DATA XREF: sub_13CF6+11w"),('0, // _byte_14f73\n','db _byte_14f73;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_158B4	db 0			; DATA XREF: sub_15577+27Dr"),('0, // _byte_158b4\n','db _byte_158b4;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_158E3	db 0			; DATA XREF: sub_15577+288w"),('0, // _byte_158e3\n','db _byte_158e3;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15912	db 0			; DATA XREF: sub_15577+28Cw"),('0, // _byte_15912\n','db _byte_15912;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15941	db 0			; DATA XREF: sub_15577+290w"),('0, // _byte_15941\n','db _byte_15941;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15970	db 0			; DATA XREF: sub_15577+294w"),('0, // _byte_15970\n','db _byte_15970;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1599F	db 0			; DATA XREF: sub_15577+298w"),('0, // _byte_1599f\n','db _byte_1599f;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_159CE	db 0			; DATA XREF: sub_15577+29Cw"),('0, // _byte_159ce\n','db _byte_159ce;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_159FD	db 0			; DATA XREF: sub_15577+2A0w"),('0, // _byte_159fd\n','db _byte_159fd;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15A2C	db 0			; DATA XREF: sub_15577+2A4w"),('0, // _byte_15a2c\n','db _byte_15a2c;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15A5B	db 0			; DATA XREF: sub_15577+2A8w"),('0, // _byte_15a5b\n','db _byte_15a5b;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15A8A	db 0			; DATA XREF: sub_15577+2ACw"),('0, // _byte_15a8a\n','db _byte_15a8a;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15AB9	db 0			; DATA XREF: sub_15577+2B0w"),('0, // _byte_15ab9\n','db _byte_15ab9;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15AE8	db 0			; DATA XREF: sub_15577+2B4w"),('0, // _byte_15ae8\n','db _byte_15ae8;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15B17	db 0			; DATA XREF: sub_15577+2B8w"),('0, // _byte_15b17\n','db _byte_15b17;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15B46	db 0			; DATA XREF: sub_15577+2BCw"),('0, // _byte_15b46\n','db _byte_15b46;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15B81	db 0			; DATA XREF: sub_15577+2C0w"),('0, // _byte_15b81\n','db _byte_15b81;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15BAD	db 0			; DATA XREF: sub_15577+2C4w"),('0, // _byte_15bad\n','db _byte_15bad;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15BDA	db 0			; DATA XREF: sub_15577+2C8w"),('0, // _byte_15bda\n','db _byte_15bda;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15C07	db 0			; DATA XREF: sub_15577+2CCw"),('0, // _byte_15c07\n','db _byte_15c07;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15C34	db 0			; DATA XREF: sub_15577+2D0w"),('0, // _byte_15c34\n','db _byte_15c34;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15C61	db 0			; DATA XREF: sub_15577+2D4w"),('0, // _byte_15c61\n','db _byte_15c61;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15C8E	db 0			; DATA XREF: sub_15577+2D8w"),('0, // _byte_15c8e\n','db _byte_15c8e;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15CBB	db 0			; DATA XREF: sub_15577+2DCw"),('0, // _byte_15cbb\n','db _byte_15cbb;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15CE8	db 0			; DATA XREF: sub_15577+2E0w"),('0, // _byte_15ce8\n','db _byte_15ce8;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15D15	db 0			; DATA XREF: sub_15577+2E4w"),('0, // _byte_15d15\n','db _byte_15d15;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15D42	db 0			; DATA XREF: sub_15577+2E8w"),('0, // _byte_15d42\n','db _byte_15d42;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15D6F	db 0			; DATA XREF: sub_15577+2ECw"),('0, // _byte_15d6f\n','db _byte_15d6f;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15D9C	db 0			; DATA XREF: sub_15577+2F0w"),('0, // _byte_15d9c\n','db _byte_15d9c;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15DC9	db 0			; DATA XREF: sub_15577+2F4w"),('0, // _byte_15dc9\n','db _byte_15dc9;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15DF6	db 0			; DATA XREF: sub_15577+2F8w"),('0, // _byte_15df6\n','db _byte_15df6;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_15E23	db 0			; DATA XREF: sub_15577+2FCw"),('0, // _byte_15e23\n','db _byte_15e23;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16379	db 0			; DATA XREF: sub_1609F+21Ar"),('0, // _byte_16379\n','db _byte_16379;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_163A8	db 0			; DATA XREF: sub_1609F+225w"),('0, // _byte_163a8\n','db _byte_163a8;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_163D7	db 0			; DATA XREF: sub_1609F+229w"),('0, // _byte_163d7\n','db _byte_163d7;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16406	db 0			; DATA XREF: sub_1609F+22Dw"),('0, // _byte_16406\n','db _byte_16406;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16435	db 0			; DATA XREF: sub_1609F+231w"),('0, // _byte_16435\n','db _byte_16435;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16493	db 0			; DATA XREF: sub_1609F+239w"),('0, // _byte_16493\n','db _byte_16493;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_164C2	db 0			; DATA XREF: sub_1609F+23Dw"),('0, // _byte_164c2\n','db _byte_164c2;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_164F1	db 0			; DATA XREF: sub_1609F+241w"),('0, // _byte_164f1\n','db _byte_164f1;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16520	db 0			; DATA XREF: sub_1609F+245w"),('0, // _byte_16520\n','db _byte_16520;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1654F	db 0			; DATA XREF: sub_1609F+249w"),('0, // _byte_1654f\n','db _byte_1654f;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1657E	db 0			; DATA XREF: sub_1609F+24Dw"),('0, // _byte_1657e\n','db _byte_1657e;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_165DC	db 0			; DATA XREF: sub_1609F+255w"),('0, // _byte_165dc\n','db _byte_165dc;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1660B	db 0			; DATA XREF: sub_1609F+259w"),('0, // _byte_1660b\n','db _byte_1660b;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16646	db 0			; DATA XREF: sub_1609F+25Dw"),('0, // _byte_16646\n','db _byte_16646;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16672	db 0			; DATA XREF: sub_1609F+261w"),('0, // _byte_16672\n','db _byte_16672;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1669F	db 0			; DATA XREF: sub_1609F+265w"),('0, // _byte_1669f\n','db _byte_1669f;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_166CC	db 0			; DATA XREF: sub_1609F+269w"),('0, // _byte_166cc\n','db _byte_166cc;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_166F9	db 0			; DATA XREF: sub_1609F+26Dw"),('0, // _byte_166f9\n','db _byte_166f9;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16726	db 0			; DATA XREF: sub_1609F+271w"),('0, // _byte_16726\n','db _byte_16726;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16753	db 0			; DATA XREF: sub_1609F+275w"),('0, // _byte_16753\n','db _byte_16753;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16780	db 0			; DATA XREF: sub_1609F+279w"),('0, // _byte_16780\n','db _byte_16780;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_167AD	db 0			; DATA XREF: sub_1609F+27Dw"),('0, // _byte_167ad\n','db _byte_167ad;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_167DA	db 0			; DATA XREF: sub_1609F+281w"),('0, // _byte_167da\n','db _byte_167da;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16807	db 0			; DATA XREF: sub_1609F+285w"),('0, // _byte_16807\n','db _byte_16807;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16834	db 0			; DATA XREF: sub_1609F+289w"),('0, // _byte_16834\n','db _byte_16834;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_16861	db 0			; DATA XREF: sub_1609F+28Dw"),('0, // _byte_16861\n','db _byte_16861;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1688E	db 0			; DATA XREF: sub_1609F+291w"),('0, // _byte_1688e\n','db _byte_1688e;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_168BB	db 0			; DATA XREF: sub_1609F+295w"),('0, // _byte_168bb\n','db _byte_168bb;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_168E8	db 0			; DATA XREF: sub_1609F+299w"),('0, // _byte_168e8\n','db _byte_168e8;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1C1B8	db 0			; DATA XREF: _int9_keybr _dosexec+58w ..."),('0, // _byte_1c1b8\n','db _byte_1c1b8;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1CCEB	db 78h			; DATA XREF: _text_init2:loc_1A6C2w"),('120, // _byte_1cceb\n','db _byte_1cceb;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1D616	db 20h			; DATA XREF: _useless_197F2+Dw"),('32, // _byte_1d616\n','db _byte_1d616;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1D66B	db 20h			; DATA XREF: _useless_197F2+18w"),('32, // _byte_1d66b\n','db _byte_1d66b;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DC0A	db 62h dup(0)		; DATA XREF: _find_mods+6Fo"),('{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, // _byte_1dc0a\n','db _byte_1dc0a[98];\n', 98))
        self.assertEqual(parser_instance.action_data(line="_byte_1DCF7	db 0FFh			; DATA XREF: _callsubx+1Cr _callsubx+55w"),('255, // _byte_1dcf7\n','db _byte_1dcf7;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DCF8	db 14h			; DATA XREF: _start+DAr	_callsubx+20r ..."),('20, // _byte_1dcf8\n','db _byte_1dcf8;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DCFB	db 4Bh			; DATA XREF: _callsubx+13r"),('75, // _byte_1dcfb\n','db _byte_1dcfb;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE70	db 0			; DATA XREF: _start+168w _start+268w ..."),('0, // _byte_1de70\n','db _byte_1de70;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE71	db 0			; DATA XREF: seg001:loc_1A934w"),('0, // _byte_1de71\n','db _byte_1de71;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE72	db 0			; DATA XREF: _keyb_screen_loop+5w"),('0, // _byte_1de72\n','db _byte_1de72;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE73	db 0			; DATA XREF: _read_module+79w"),('0, // _byte_1de73\n','db _byte_1de73;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE74	db 0			; DATA XREF: _keyb_screen_loop+9w"),('0, // _byte_1de74\n','db _byte_1de74;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE75	db 0			; DATA XREF: _keyb_screen_loop+Cw"),('0, // _byte_1de75\n','db _byte_1de75;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE76	db 0			; DATA XREF: _keyb_screen_loop+10w"),('0, // _byte_1de76\n','db _byte_1de76;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE78	db 0			; DATA XREF: _read_module+8Bw"),('0, // _byte_1de78\n','db _byte_1de78;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE79	db 0			; DATA XREF: _video_prp_mtr_positn+2w"),('0, // _byte_1de79\n','db _byte_1de79;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE7A	db 0			; DATA XREF: _video_prp_mtr_positn+7w"),('0, // _byte_1de7a\n','db _byte_1de7a;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE7B	db 0			; DATA XREF: _read_module+96w"),('0, // _byte_1de7b\n','db _byte_1de7b;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE7C	db 0			; DATA XREF: _start:loc_193BCr"),('0, // _byte_1de7c\n','db _byte_1de7c;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE7D	db 0			; DATA XREF: _start+32Fw _start+34Ar ..."),('0, // _byte_1de7d\n','db _byte_1de7d;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE7E	db 0			; DATA XREF: _start+1B9w _start+217r ..."),('0, // _byte_1de7e\n','db _byte_1de7e;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE7F	db 0			; DATA XREF: _start+260w _start+2F0r ..."),('0, // _byte_1de7f\n','db _byte_1de7f;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE81	db 0			; DATA XREF: _spectr_1BBC1+20r"),('0, // _byte_1de81\n','db _byte_1de81;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE82	db 0			; DATA XREF: _start+E1w"),('0, // _byte_1de82\n','db _byte_1de82;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE83	db 3			; DATA XREF: _start+E7w"),('3, // _byte_1de83\n','db _byte_1de83;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE84	db 0			; DATA XREF: _read_module+65w"),('0, // _byte_1de84\n','db _byte_1de84;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE85	db 0			; DATA XREF: _keyb_screen_loop+2EBw"),('0, // _byte_1de85\n','db _byte_1de85;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE86	db 0			; DATA XREF: _start+D7w	_text_init2r ..."),('0, // _byte_1de86\n','db _byte_1de86;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_1DE90	db 0			; DATA XREF: _start:loc_193C7r"),('0, // _byte_1de90\n','db _byte_1de90;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_24629	db 20h			; DATA XREF: _someplaymode+64r"),('32, // _byte_24629\n','db _byte_24629;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_257DA	db 10h			; DATA XREF: _useless_writeinr+3Fw"),('16, // _byte_257da\n','db _byte_257da;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_280E7	db ?			; DATA XREF: _s3m_module+1F3w"),('0, // _byte_280e7\n','db _byte_280e7;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_282E8	db 20h dup( ?)		; DATA XREF: _clean_11C43+AEo"),('{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, // _byte_282e8\n','db _byte_282e8[32];\n', 32))
        self.assertEqual(parser_instance.action_data(line="_byte_30577	db ?			; DATA XREF: _e669_module+32r"),('0, // _byte_30577\n','db _byte_30577;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_30579	db 21h dup( ?)		; DATA XREF: _e669_module:loc_1096Fr"),('{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, // _byte_30579\n','db _byte_30579[33];\n', 33))
        self.assertEqual(parser_instance.action_data(line="_byte_30639	db ?			; DATA XREF: _ult_module+169r"),('0, // _byte_30639\n','db _byte_30639;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_byte_3150A	db ?			; DATA XREF: _psm_module+139r"),('0, // _byte_3150a\n','db _byte_3150a;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_cfg_buffer	db    4			; DATA XREF: _loadcfg+Co _loadcfg+1Er"),('4, // _cfg_buffer\n','db _cfg_buffer;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_chrin		dd ?			; DATA XREF: _moduleread:loc_10033o"),('0, // _chrin\n','dd _chrin;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_config_word	dw 0			; DATA XREF: _ems_init+8r"),('0, // _config_word\n','dw _config_word;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_configword	dw 218Bh		; DATA XREF: _start+60w	_start+6Cw ..."),('8587, // _configword\n','dw _configword;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_covox_txt	db    2			; DATA XREF: seg003:0D7Co seg003:0D7Eo"),('2, // _covox_txt\n','db _covox_txt;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_critsectpoint_off dw 0			; DATA XREF: _start+150w"),('0, // _critsectpoint_off\n','dw _critsectpoint_off;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_critsectpoint_seg dw 0			; DATA XREF: _start+154w"),('0, // _critsectpoint_seg\n','dw _critsectpoint_seg;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_current_patterns dw 0			; DATA XREF: _read_module+5Fw"),('0, // _current_patterns\n','dw _current_patterns;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_dma_buf_pointer	dd 0			; DATA XREF: _mod_readfile_11F4E+9Cw"),('0, // _dma_buf_pointer\n','dd _dma_buf_pointer;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dma_channel	db 0			; DATA XREF: _read_sndsettings+11r"),('0, // _dma_channel\n','db _dma_channel;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_dma_channel2	db 0			; DATA XREF: _wss_init:loc_147DCw"),('0, // _dma_channel2\n','db _dma_channel2;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_dma_channel_0	db 0			; DATA XREF: _mod_readfile_11F4E+8Er"),('0, // _dma_channel_0\n','db _dma_channel_0;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_dma_channel_1	db 0FFh			; DATA XREF: _callsubx+Br _callsubx+4Dw"),('255, // _dma_channel_1\n','db _dma_channel_1;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_dma_chn_mask	db 0			; DATA XREF: _sb16_init+4Bw"),('0, // _dma_chn_mask\n','db _dma_chn_mask;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_dma_mode	db 0			; DATA XREF: _proaud_set+3w _wss_set+3w	..."),('0, // _dma_mode\n','db _dma_mode;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_dword_1DCEC	dd 10524E49h		; DATA XREF: _loadcfg+1Ar"),('273829449, // _dword_1dcec\n','dd _dword_1dcec;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_1DE2C	dd 0			; DATA XREF: _text_init2+22Aw"),('0, // _dword_1de2c\n','dd _dword_1de2c;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_1DE88	dd 0			; DATA XREF: _start+7DBr _start+7E2w ..."),('0, // _dword_1de88\n','dd _dword_1de88;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244C8	dd 0			; DATA XREF: _spectr_1B084+39w"),('0, // _dword_244c8\n','dd _dword_244c8;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244D4	dd 0			; DATA XREF: _spectr_1B084+3Dw"),('0, // _dword_244d4\n','dd _dword_244d4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244E4	dd 0			; DATA XREF: _spectr_1B084+8Bw"),('0, // _dword_244e4\n','dd _dword_244e4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244E8	dd 0			; DATA XREF: _spectr_1B084+9Aw"),('0, // _dword_244e8\n','dd _dword_244e8;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244EC	dd 0			; DATA XREF: _spectr_1B084+A9w"),('0, // _dword_244ec\n','dd _dword_244ec;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244F0	dd 0			; DATA XREF: _spectr_1B084+B6w"),('0, // _dword_244f0\n','dd _dword_244f0;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244F4	dd 0			; DATA XREF: _spectr_1B084+66w"),('0, // _dword_244f4\n','dd _dword_244f4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244F8	dd 0			; DATA XREF: _spectr_1B084+6Ew"),('0, // _dword_244f8\n','dd _dword_244f8;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_244FC	dd 0			; DATA XREF: _spectr_1B084+CBw"),('0, // _dword_244fc\n','dd _dword_244fc;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_24500	dd 0			; DATA XREF: _spectr_1B084+DBw"),('0, // _dword_24500\n','dd _dword_24500;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_24504	dd 0			; DATA XREF: _spectr_1B084+100w"),('0, // _dword_24504\n','dd _dword_24504;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_24508	dd 0			; DATA XREF: _spectr_1B084+F0w"),('0, // _dword_24508\n','dd _dword_24508;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_245BC	dd 0			; DATA XREF: _someplaymode+59w"),('0, // _dword_245bc\n','dd _dword_245bc;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_245C0	dd 0			; DATA XREF: _someplaymode:loc_12C3Cw"),('0, // _dword_245c0\n','dd _dword_245c0;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_245C4	dd 0			; DATA XREF: _mod_n_t_module:loc_101F4r"),('0, // _dword_245c4\n','dd _dword_245c4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_2463C	dd 0			; DATA XREF: _someplaymode+8Aw"),('0, // _dword_2463c\n','dd _dword_2463c;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_24640	dd 0			; DATA XREF: _memfree_125DA+13w"),('0, // _dword_24640\n','dd _dword_24640;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_24684	dd 0			; DATA XREF: _alloc_dma_bufw"),('0, // _dword_24684\n','dd _dword_24684;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_24694	dd 0			; DATA XREF: _dma_186E3+5Dr"),('0, // _dword_24694\n','dd _dword_24694;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_257A0	dd 0			; DATA XREF: _useless_writeinr+170w"),('0, // _dword_257a0\n','dd _dword_257a0;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_25886	dd 0			; DATA XREF: _useless_writeinr_118+59w"),('0, // _dword_25886\n','dd _dword_25886;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_25892	dd 0			; DATA XREF: _useless_writeinr_118+31w"),('0, // _dword_25892\n','dd _dword_25892;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_25896	dd 0			; DATA XREF: _useless_writeinr_118+39w"),('0, // _dword_25896\n','dd _dword_25896;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_27BC8	dd ?			; DATA XREF: _moduleread+8Eo"),('0, // _dword_27bc8\n','dd _dword_27bc8;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_27BCC	dd ?			; DATA XREF: _e669_module+4Ew"),('0, // _dword_27bcc\n','dd _dword_27bcc;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_30518	dd ?			; DATA XREF: _ult_module:loc_113F8o"),('0, // _dword_30518\n','dd _dword_30518;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_3055A	dd ?			; DATA XREF: _psm_module+105r"),('0, // _dword_3055a\n','dd _dword_3055a;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_30566	dd ?			; DATA XREF: _psm_module+55r"),('0, // _dword_30566\n','dd _dword_30566;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_dword_3063D	dd ?			; DATA XREF: _ult_module+225r"),('0, // _dword_3063d\n','dd _dword_3063d;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_eModuleNotFound	db 'Module not found',0Dh,0Ah,0 ; DATA XREF: _moduleread+1Co"),('"Module not found\\r\\n", // _emodulenotfound\n','char _emodulenotfound[19];\n', 19))

        #self.assertEqual(parser_instance.action_data(line="_effoff_18F60	dw offset _eff_nullsub	; DATA XREF: sub_137D5+16r"),('k_eff_nullsub, // _effoff_18f60\n','dw _effoff_18f60;\n', 2))

        self.assertEqual(parser_instance.action_data(line="_ems_enabled	db 0			; DATA XREF: _ems_initw	_ems_init+78w ..."),('0, // _ems_enabled\n','db _ems_enabled;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_ems_handle	dw 0			; DATA XREF: _ems_init+74w"),('0, // _ems_handle\n','dw _ems_handle;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_ems_log_pagenum	dw 0			; DATA XREF: _ems_init+7Dw"),('0, // _ems_log_pagenum\n','dw _ems_log_pagenum;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_ems_pageframe	dw 0			; DATA XREF: _useless_11787+3Er"),('0, // _ems_pageframe\n','dw _ems_pageframe;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_esseg_atstart	dw 0			; DATA XREF: _start+5w _parse_cmdline+7r ..."),('0, // _esseg_atstart\n','dw _esseg_atstart;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_f1_help_text	dw 3F8h			; DATA XREF: seg001:1CD8o"),('1016, // _f1_help_text\n','dw _f1_help_text;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_fhandle_1DE68	dw 0			; DATA XREF: _init_vga_waves+42w"),('0, // _fhandle_1de68\n','dw _fhandle_1de68;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_fhandle_module	dw 0			; DATA XREF: _moduleread+19w"),('0, // _fhandle_module\n','dw _fhandle_module;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_flag_playsetttings db 0			; DATA XREF: _clean_11C43+68r"),('0, // _flag_playsetttings\n','db _flag_playsetttings;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_flg_play_settings db 0			; DATA XREF: _keyb_screen_loop+2Fw"),('0, // _flg_play_settings\n','db _flg_play_settings;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_frameborder	db '      ██████╔╗╚╝═║┌┐└┘─│╓╖╙╜─║╒╕╘╛═│',0 ; DATA XREF: _draw_frame+3Do"),('"      ██████╔╗╚╝═║┌┐└┘─│╓╖╙╜─║╒╕╘╛═│", // _frameborder\n','char _frameborder[37];\n', 37))
        self.assertEqual(parser_instance.action_data(line="_freq1		dw 22050		; DATA XREF: _volume_prepare_waves+48r"),('22050, // _freq1\n','dw _freq1;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_freq2		dw 0			; DATA XREF: _read_sndsettings+2Cr"),('0, // _freq2\n','dw _freq2;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_freq_1DCF6	db 2Ch			; DATA XREF: _callsubx+Fr _callsubx+51w"),('44, // _freq_1dcf6\n','db _freq_1dcf6;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_freq_245DE	dw 0			; DATA XREF: _mod_1024A+40r"),('0, // _freq_245de\n','dw _freq_245de;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_freq_246D7	db 0			; DATA XREF: _read_sndsettings+15r"),('0, // _freq_246d7\n','db _freq_246d7;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_gravis_port	dw 0			; DATA XREF: _volume_prep+61r"),('0, // _gravis_port\n','dw _gravis_port;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_gravis_txt	db    1			; DATA XREF: seg003:_sndcards_text_tblo"),('1, // _gravis_txt\n','db _gravis_txt;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_hopeyoulike	dw 3C6h			; DATA XREF: _start+204o"),('966, // _hopeyoulike\n','dw _hopeyoulike;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_int1Avect	dd 0			; DATA XREF: _int1a_timer+12r"),('0, // _int1avect\n','dd _int1avect;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_int8addr	dd 0			; DATA XREF: sub_12DA8+6Aw"),('0, // _int8addr\n','dd _int8addr;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_interrupt_mask	dw 0			; DATA XREF: _setsnd_handler+Cw"),('0, // _interrupt_mask\n','dw _interrupt_mask;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_intvectoffset	dw 0			; DATA XREF: _setsnd_handler+2Dw"),('0, // _intvectoffset\n','dw _intvectoffset;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_irq_number	db 0			; DATA XREF: _read_sndsettings+Dr"),('0, // _irq_number\n','db _irq_number;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_irq_number2	db 0			; DATA XREF: _wss_init:loc_147D0w"),('0, // _irq_number2\n','db _irq_number2;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_irq_number_0	db 0			; DATA XREF: _gravis_init+35w"),('0, // _irq_number_0\n','db _irq_number_0;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_irq_number_1	db 0FFh			; DATA XREF: _callsubx+7r _callsubx+49w"),('255, // _irq_number_1\n','db _irq_number_1;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_is_stereo	db 0			; DATA XREF: sub_1265D+33r"),('0, // _is_stereo\n','db _is_stereo;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_key_code	dw 0			; DATA XREF: _start:loc_193FFr"),('0, // _key_code\n','dw _key_code;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_keyb_switches	dw 0			; DATA XREF: _start+5D8r"),('0, // _keyb_switches\n','dw _keyb_switches;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_memflg_2469A	db 0			; DATA XREF: _alloc_dma_buf+8w"),('0, // _memflg_2469a\n','db _memflg_2469a;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_messagepointer	dd 0			; DATA XREF: _start+228r _start+23Dw ..."),('0, // _messagepointer\n','dd _messagepointer;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_midi_txt	db    2			; DATA XREF: seg003:0D84o"),('2, // _midi_txt\n','db _midi_txt;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_mod_channels_number	dw 0			; DATA XREF: _moduleread+81r"),('0, // _mod_channels_number\n','dw _mod_channels_number;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_module_type_text dd 20202020h		; DATA XREF: _mod_n_t_modulew"),('538976288, // _module_type_text\n','dd _module_type_text;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_module_type_txt	db '    '               ; DATA XREF: _read_module+6Fw"),("{' ',' ',' ',' '}, // _module_type_txt\n",'char _module_type_txt[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="_moduleflag_246D0 dw 0			; DATA XREF: _mod_n_t_module+3Dw"),('0, // _moduleflag_246d0\n','dw _moduleflag_246d0;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_mouse_exist_flag db 0			; DATA XREF: _mouse_init:loc_1C6EFw"),('0, // _mouse_exist_flag\n','db _mouse_exist_flag;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_mouse_visible	db 0Ah dup(0)		; DATA XREF: _mouse_initw"),('{0,0,0,0,0,0,0,0,0,0}, // _mouse_visible\n','db _mouse_visible[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_mousecolumn	dw 0			; DATA XREF: _start+7A0r _start+7BCr ..."),('0, // _mousecolumn\n','dw _mousecolumn;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_mouserow	dw 0			; DATA XREF: _start+7A3r _start+7BFr ..."),('0, // _mouserow\n','dw _mouserow;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_msg		db 'Searching directory for modules  ',0 ; DATA XREF: _start+2F7o"),('"Searching directory for modules  ", // _msg\n','char _msg[34];\n', 34))
        self.assertEqual(parser_instance.action_data(line="_multip_244CC	dd 0			; DATA XREF: _spectr_1B084+2Fw"),('0, // _multip_244cc\n','dd _multip_244cc;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_multip_244D0	dd 0			; DATA XREF: _spectr_1B084+25w"),('0, // _multip_244d0\n','dd _multip_244d0;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_my_in		db ?			; DATA XREF: __2stm_module+50o"),('0, // _my_in\n','db _my_in;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_my_seg_index	dw 0			; DATA XREF: _psm_module+136r"),('0, // _my_seg_index\n','dw _my_seg_index;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_my_size		dw 0			; DATA XREF: _volume_prep+9w"),('0, // _my_size\n','dw _my_size;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_myendl		db 0Dh,0Ah,'$'          ; DATA XREF: _start-1Do"),("{'\\r','\\n','$'}, // _myendl\n",'char _myendl[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_myin		dd ?			; DATA XREF: _mtm_module+22o"),('0, // _myin\n','dd _myin;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_myin_0		db ?			; DATA XREF: _ult_module+3Ao"),('0, // _myin_0\n','db _myin_0;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_myseg_24698	dw 0			; DATA XREF: _alloc_dma_buf+31w"),('0, // _myseg_24698\n','dw _myseg_24698;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_mystr		db 42h dup(0)		; DATA XREF: _start:loc_192E0o"),('{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, // _mystr\n','db _mystr[66];\n', 66))
        self.assertEqual(parser_instance.action_data(line="_notes		db '  C-C#D-D#E-F-F#G-G#A-A#B-' ; DATA XREF: seg001:1930r"),("{' ',' ','C','-','C','#','D','-','D','#','E','-','F','-','F','#','G','-','G','#','A','-','A','#','B','-'}, // _notes\n",'char _notes[26];\n', 26))
        #self.assertEqual(parser_instance.action_data(line="_offs_draw	dw offset loc_19050	; DATA XREF: _keyb_screen_loop+32r"),('kloc_19050, // _offs_draw\n','dw _offs_draw;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_oint24_1C1AC	dd 0			; DATA XREF: _start+115w _start+1D4r ..."),('0, // _oint24_1c1ac\n','dd _oint24_1c1ac;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_oint2f_1C1B4	dd 0			; DATA XREF: _start+124w _start+1C8r ..."),('0, // _oint2f_1c1b4\n','dd _oint2f_1c1b4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_oint8off_1DE14	dw 0			; DATA XREF: _start+F9w"),('0, // _oint8off_1de14\n','dw _oint8off_1de14;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_oint8seg_1DE16	dw 0			; DATA XREF: _start+FDw"),('0, // _oint8seg_1de16\n','dw _oint8seg_1de16;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_oint9_1C1A4	dd 0			; DATA XREF: _start+106w _start+1E0r ..."),('0, // _oint9_1c1a4\n','dd _oint9_1c1a4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_old_intprocoffset dw 0			; DATA XREF: _setsnd_handler+3Aw"),('0, // _old_intprocoffset\n','dw _old_intprocoffset;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_old_intprocseg	dw 0			; DATA XREF: _setsnd_handler+3Ew"),('0, // _old_intprocseg\n','dw _old_intprocseg;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_outp_freq	dw 0			; DATA XREF: _read_module+82w"),('0, // _outp_freq\n','dw _outp_freq;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_palette_24404	db    0			; DATA XREF: _init_vga_waves+17o"),('0, // _palette_24404\n','db _palette_24404;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_pc_timer_tbl	db 40h,40h,40h,40h,40h,40h,40h,40h,40h,40h,3Fh,3Fh,3Fh"),('{64,64,64,64,64,64,64,64,64,64,63,63,63}, // _pc_timer_tbl\n','db _pc_timer_tbl[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_pcspeaker_txt	db    2			; DATA XREF: seg003:0D80o seg003:0D82o"),('2, // _pcspeaker_txt\n','db _pcspeaker_txt;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_play_state	db 0			; DATA XREF: _getset_playstate+Bw"),('0, // _play_state\n','db _play_state;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_pointer_245B4	dd 0			; DATA XREF: sub_135CA+1Cr"),('0, // _pointer_245b4\n','dd _pointer_245b4;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_prev_scan_code	db 0			; DATA XREF: _int9_keyb+19r"),('0, // _prev_scan_code\n','db _prev_scan_code;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_s3mtable_108D6	db 0FFh,10h,0Bh,0Dh,15h,12h,11h,13h,14h,1Bh,1Dh,17h,16h"),('{255,16,11,13,21,18,17,19,20,27,29,23,22}, // _s3mtable_108d6\n','db _s3mtable_108d6[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_s3mtable_108F0	db 0,3,5,4,7,0FFh,0FFh,0FFh,8,0FFh,0FFh,6,0Ch,0Dh,0FFh"),('{0,3,5,4,7,255,255,255,8,255,255,6,12,13,255}, // _s3mtable_108f0\n','db _s3mtable_108f0[15];\n', 15))
        self.assertEqual(parser_instance.action_data(line="_sIplay_cfg	db 'IPLAY.CFG',0     ; DATA XREF: _loadcfgo"),('"IPLAY.CFG", // _siplay_cfg\n','char _siplay_cfg[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_samples_outoffs_24600	dw 0			; DATA XREF: sub_12EBA+2Cw"),('0, // _samples_outoffs_24600\n','dw _samples_outoffs_24600;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_savesp_245D0	dw 0			; DATA XREF: _moduleread+15w"),('0, // _savesp_245d0\n','dw _savesp_245d0;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_sb16_txt	db    2			; DATA XREF: seg003:0D72o seg003:0D74o ..."),('2, // _sb16_txt\n','db _sb16_txt;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_sb_base_port	dw 0			; DATA XREF: _sb16_on+17r _sb16_on+44r ..."),('0, // _sb_base_port\n','dw _sb_base_port;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_sb_int_counter	db 0			; DATA XREF: _sb_test_interruptw"),('0, // _sb_int_counter\n','db _sb_int_counter;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_sb_irq_number	db 0			; DATA XREF: _sb16_init+1Cw"),('0, // _sb_irq_number\n','db _sb_irq_number;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_sb_timeconst	db 0			; DATA XREF: _sbpro_init+51w _sb_set-D1r ..."),('0, // _sb_timeconst\n','db _sb_timeconst;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_segfsbx_1DE28	dd 0			; DATA XREF: _read_module+99w"),('0, // _segfsbx_1de28\n','dd _segfsbx_1de28;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_slider		db '─\|/─\|/'           ; DATA XREF: _modules_search+7Fr"),("{'\\xc4','\\\\','\\\\','|','/','\\xc4','\\\\','\\\\','|','/'}, // _slider\n",'char _slider[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="_snd_base_port	dw 0			; DATA XREF: _read_sndsettings+9r"),('0, // _snd_base_port\n','dw _snd_base_port;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_snd_base_port_0	dw 0FFFFh		; DATA XREF: _callsubx+3r _callsubx+45w"),('65535, // _snd_base_port_0\n','dw _snd_base_port_0;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_snd_card_type	db 3			; DATA XREF: _text_init2+18Er"),('3, // _snd_card_type\n','db _snd_card_type;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_snd_cards_offs	dw offset _aGravisUltrasoun ; DATA XREF:	seg003:114Eo"),('offset(default_seg,_agravisultrasoun), // _snd_cards_offs\n','dw _snd_cards_offs;\n',2))
        self.assertEqual(parser_instance.action_data(line="_snd_init	db 0			; DATA XREF: sub_12D05+Br"),('0, // _snd_init\n','db _snd_init;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_snd_set_flag	db 0			; DATA XREF: sub_12DA8+60w _snd_on+7r ..."),('0, // _snd_set_flag\n','db _snd_set_flag;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_sndcard_type	db 0			; DATA XREF: _mtm_module+2Er"),('0, // _sndcard_type\n','db _sndcard_type;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_sndflags_24622	db 0			; DATA XREF: _useless_11787+9r"),('0, // _sndflags_24622\n','db _sndflags_24622;\n', 1))
        self.assertEqual(parser_instance.action_data(line="_sound_port	dw 0			; DATA XREF: _proaud_init+42w"),('0, // _sound_port\n','dw _sound_port;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_swapdata_off	dw 0			; DATA XREF: _start+161w"),('0, // _swapdata_off\n','dw _swapdata_off;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_swapdata_seg	dw 0			; DATA XREF: _start+165w"),('0, // _swapdata_seg\n','dw _swapdata_seg;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_table_13EC3	db 140,50,25,15,10,7,6,4,3,3,2,2,2,2,1,1 ; DATA	XREF: sub_13E9B+Dr"),('{140,50,25,15,10,7,6,4,3,3,2,2,2,2,1,1}, // _table_13ec3\n','db _table_13ec3[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_table_14057	db 0FFh,80h,40h,2Ah,20h,19h,15h,12h,10h,0Eh,0Ch,0Bh,0Ah"),('{255,128,64,42,32,25,21,18,16,14,12,11,10}, // _table_14057\n','db _table_14057[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_table_246F6	dw 8363,8422,8482,8543,8604,8667,8730,8794,7901,7954,8007"),('{8363,8422,8482,8543,8604,8667,8730,8794,7901,7954,8007}, // _table_246f6\n','dw _table_246f6[11];\n', 22))
        self.assertEqual(parser_instance.action_data(line="_table_24716	dw 8000h,9000h,0A000h,0A952h,0B000h,0B521h,0B952h,0BCDEh"),('{32768,36864,40960,43346,45056,46369,47442,48350}, // _table_24716\n','dw _table_24716[8];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_table_24798	dw 8000h,9800h,0A000h,0A800h,0B000h,0B400h,0B800h,0BC00h"),('{32768,38912,40960,43008,45056,46080,47104,48128}, // _table_24798\n','dw _table_24798[8];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_table_24818	dw 8000h,9800h,0A000h,0A800h,0B000h,0B400h,0B800h,0BC00h"),('{32768,38912,40960,43008,45056,46080,47104,48128}, // _table_24818\n','dw _table_24818[8];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_table_24898	db 1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh,1Eh"),('{30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30}, // _table_24898\n','db _table_24898[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="_table_25118	dw 1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,856,808,762,720,678,640,604,570,538,508,480,453"),('{1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,856,808,762,720,678,640,604,570,538,508,480,453}, // _table_25118\n','dw _table_25118[24];\n', 48))
        self.assertEqual(parser_instance.action_data(line="_table_251C0	db  0,18h,31h,4Ah,61h,78h,8Dh,0A1h,0B4h,0C5h,0D4h,0E0h"),('{0,24,49,74,97,120,141,161,180,197,212,224}, // _table_251c0\n','db _table_251c0[12];\n', 12))
        self.assertEqual(parser_instance.action_data(line="_table_251E0	db  0,15h,20h,29h,30h,37h,3Dh,44h,49h,4Fh,54h,59h,5Eh"),('{0,21,32,41,48,55,61,68,73,79,84,89,94}, // _table_251e0\n','db _table_251e0[13];\n', 13))
        self.assertEqual(parser_instance.action_data(line="_table_25221	db  0, 4, 8,0Ch,10h,14h,18h,1Ch,20h,24h,28h,2Ch,30h,34h"),('{0,4,8,12,16,20,24,28,32,36,40,44,48,52}, // _table_25221\n','db _table_25221[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="_table_25261	db  0, 4, 8,0Ch,10h,14h,18h,1Ch,20h,24h,28h,2Ch,30h,34h"),('{0,4,8,12,16,20,24,28,32,36,40,44,48,52}, // _table_25261\n','db _table_25261[14];\n', 14))

        #self.assertEqual(parser_instance.action_data(line="_table_sndcrdname dw offset _aGravisUltrasou ; DATA XREF:	_text_init2+19Dr"),('0, // _table_sndcrdname\n','dw _table_sndcrdname;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_tabledword_24526 dd    0,65536,46340,25079,12785,6423,3215,1608, 804, 402"),('{0,65536,46340,25079,12785,6423,3215,1608,804,402}, // _tabledword_24526\n','dd _tabledword_24526[10];\n', 40))
        self.assertEqual(parser_instance.action_data(line="_tabledword_24562 dd -131072,-65536,-19196,-4989,-1260,-316, -79, -20,  -5"),('{4294836224,4294901760,4294948100,4294962307,4294966036,4294966980,4294967217,4294967276,4294967291}, // _tabledword_24562\n','dd _tabledword_24562[9];\n', 36))
        self.assertEqual(parser_instance.action_data(line="_timer_word_14F6E dw 0			; DATA XREF: _set_timerw _text:4F59r"),('0, // _timer_word_14f6e\n','dw _timer_word_14f6e;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_vga_palette	db 0,0,0		; DATA XREF: _init_vga_waves+1Fo"),('{0,0,0}, // _vga_palette\n','db _vga_palette[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="_videomempointer	dd 0			; DATA XREF: _start:loc_1917Dw"),('0, // _videomempointer\n','dd _videomempointer;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_videopoint_shiftd dd 0			; DATA XREF: _text_init2+5Fw"),('0, // _videopoint_shiftd\n','dd _videopoint_shiftd;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_volume_1DE34	dd 0			; DATA XREF: _read_module+DAw"),('0, // _volume_1de34\n','dd _volume_1de34;\n', 4))
        self.assertEqual(parser_instance.action_data(line="_volume_245FC	dw 100h			; DATA XREF: sub_1265D+5r"),('256, // _volume_245fc\n','dw _volume_245fc;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_14913	dw 536h			; DATA XREF: _wss_set+14w"),('1334, // _word_14913\n','dw _word_14913;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_14BBB	dw 22Fh			; DATA XREF: _sb16_on+49w _sb16_on+57w"),('559, // _word_14bbb\n','dw _word_14bbb;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_14CEB	dw 22Eh			; DATA XREF: _sb_set-108w"),('558, // _word_14ceb\n','dw _word_14ceb;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_14FC0	dw 1000h		; DATA XREF: _covox_init+33w"),('4096, // _word_14fc0\n','dw _word_14fc0;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_14FC5	dw 1234h		; DATA XREF: _covox_init+37w"),('4660, // _word_14fc5\n','dw _word_14fc5;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_14FC8	dw 378h			; DATA XREF: _covox_init+24w"),('888, // _word_14fc8\n','dw _word_14fc8;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1504D	dw 37Ah			; DATA XREF: _stereo_init+27w"),('890, // _word_1504d\n','dw _word_1504d;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_15056	dw 1234h		; DATA XREF: _stereo_init+3Aw"),('4660, // _word_15056\n','dw _word_15056;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_15126	dw 1234h		; DATA XREF: _adlib_init+75w"),('4660, // _word_15126\n','dw _word_15126;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1519B	dw 1000h		; DATA XREF: _pcspeaker_init+1Ew"),('4096, // _word_1519b\n','dw _word_1519b;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_151A3	dw 1234h		; DATA XREF: _pcspeaker_init+22w"),('4660, // _word_151a3\n','dw _word_151a3;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1D26D	dw 3F2h			; DATA XREF: _dosexec+19o"),('1010, // _word_1d26d\n','dw _word_1d26d;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1D3B0	dw 49Eh			; DATA XREF: _start+723o"),('1182, // _word_1d3b0\n','dw _word_1d3b0;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1D614	dw 2020h		; DATA XREF: _useless_197F2+7w"),('8224, // _word_1d614\n','dw _word_1d614;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1D669	dw 2020h		; DATA XREF: _useless_197F2+12w"),('8224, // _word_1d669\n','dw _word_1d669;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_1DE46	dw 0			; DATA XREF: _keyb_screen_loop+316r"),('0, // _word_1de46\n','dw _word_1de46;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_246DE	dw 6B00h,6500h,5F40h,5A00h,54C0h,5000h,4B80h,4740h,4340h"),('{27392,25856,24384,23040,21696,20480,19328,18240,17216}, // _word_246de\n','dw _word_246de[9];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_word_24998	dw 6B00h,6500h,5F40h,5A00h,54C0h,5000h,4B80h,4740h,4340h"),('{27392,25856,24384,23040,21696,20480,19328,18240,17216}, // _word_24998\n','dw _word_24998[9];\n', 18))
        self.assertEqual(parser_instance.action_data(line="_word_257A4	dw 0			; DATA XREF: _useless_writeinr+106w"),('0, // _word_257a4\n','dw _word_257a4;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_257E6	dw 4			; DATA XREF: _useless_writeinr+53w"),('4, // _word_257e6\n','dw _word_257e6;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_257E8	dw 0			; DATA XREF: _useless_writeinr+59w"),('0, // _word_257e8\n','dw _word_257e8;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_257EA	dw 0			; DATA XREF: _useless_writeinr+5Fw"),('0, // _word_257ea\n','dw _word_257ea;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_257EC	dw 0			; DATA XREF: _useless_writeinr+65w"),('0, // _word_257ec\n','dw _word_257ec;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_257EE	dw 0			; DATA XREF: _useless_writeinr+6Bw"),('0, // _word_257ee\n','dw _word_257ee;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_257F0	dw 0			; DATA XREF: _useless_writeinr+71w"),('0, // _word_257f0\n','dw _word_257f0;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_2588E	dw 0			; DATA XREF: _useless_writeinr_118+40w"),('0, // _word_2588e\n','dw _word_2588e;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30515	dw ?			; DATA XREF: _ult_module+1Ar"),('0, // _word_30515\n','dw _word_30515;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30520	dw ?			; DATA XREF: _snd_off-3644r"),('0, // _word_30520\n','dw _word_30520;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30524	dw ?			; DATA XREF: _snd_off-3534r"),('0, // _word_30524\n','dw _word_30524;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_3052A	dw ?			; DATA XREF: _s3m_module+D0r"),('0, // _word_3052a\n','dw _word_3052a;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_3052C	dw ?			; DATA XREF: _s3m_module+DEr"),('0, // _word_3052c\n','dw _word_3052c;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30532	dw ?			; DATA XREF: _s3m_module+24r"),('0, // _word_30532\n','dw _word_30532;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30552	dw ?			; DATA XREF: _psm_module+35r"),('0, // _word_30552\n','dw _word_30552;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30554	dw ?			; DATA XREF: _psm_module+15r"),('0, // _word_30554\n','dw _word_30554;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30556	dw ?			; DATA XREF: _psm_module+Fr"),('0, // _word_30556\n','dw _word_30556;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30562	dw ?			; DATA XREF: _psm_module+10Cr"),('0, // _word_30562\n','dw _word_30562;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_30564	dw ?			; DATA XREF: _psm_module+110r"),('0, // _word_30564\n','dw _word_30564;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_3063B	dw ?			; DATA XREF: _ult_module+192o"),('0, // _word_3063b\n','dw _word_3063b;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_word_31508	dw ?			; DATA XREF: _mod_read_10311+5o"),('0, // _word_31508\n','dw _word_31508;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_wss_freq_table	dw 5513			; DATA XREF: _wss_test+3Er"),('5513, // _wss_freq_table\n','dw _wss_freq_table;\n', 2))
        self.assertEqual(parser_instance.action_data(line="_wss_freq_table2	dw  1,19D7h,0Fh,1F40h, 0,2580h,0Eh,2B11h, 3,3E80h, 2,49D4h"),('{1,6615,15,8000,0,9600,14,11025,3,16000,2,18900}, // _wss_freq_table2\n','dw _wss_freq_table2[12];\n', 24))
        self.assertEqual(parser_instance.action_data(line="_x_storage	dw  0, 0, 0, 0,	0, 0, 0, 0, 0, 0, 0, 0,	0, 0, 0, 0, 0"),('{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, // _x_storage\n','dw _x_storage[17];\n', 34))
        self.assertEqual(parser_instance.action_data(line="a db 0ffh,0dfh,0h"),('{255,223,0}, // a\n','db a[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="asc_1058C	db 0,18h,0Bh,0Dh,0Ah	; DATA XREF: __2stm_module+171r"),('{0,24,11,13,10}, // asc_1058c\n','db asc_1058c[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="asc_182C3	db 0,0,1,3,0,2,0,4,0,0,0,5,6,0,0,7 ; DATA XREF:	_gravis_18216+5r"),('{0,0,1,3,0,2,0,4,0,0,0,5,6,0,0,7}, // asc_182c3\n','db asc_182c3[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="asc_182D3	db 0,1,0,2,0,3,4,5	; DATA XREF: _gravis_18216+19r"),('{0,1,0,2,0,3,4,5}, // asc_182d3\n','db asc_182d3[8];\n', 8))
        self.assertEqual(parser_instance.action_data(line="asc_1CC2D	db '                              ' ; DATA XREF: _read_module+A3o"),("{' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '}, // asc_1cc2d\n",'char asc_1cc2d[30];\n', 30))
        self.assertEqual(parser_instance.action_data(line="asc_1D6E0	db '               ',0  ; DATA XREF: seg001:1A80o"),('"               ", // asc_1d6e0\n','char asc_1d6e0[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="asc_1DA00	db '                      ',0 ; DATA XREF: _modules_search:loc_19BDDo"),('"                      ", // asc_1da00\n','char asc_1da00[23];\n', 23))
        self.assertEqual(parser_instance.action_data(line="asc_246B0	db '                                ' ; DATA XREF: _mod_1021E+22o"),("{' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '}, // asc_246b0\n",'char asc_246b0[32];\n', 32))
        self.assertEqual(parser_instance.action_data(line="asc_25856	db '                                ',0Dh,0Ah,1Ah"),("{' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','\\r','\\n',26}, // asc_25856\n",'char asc_25856[35];\n', 35))
        self.assertEqual(parser_instance.action_data(line="audio_len	dw 0			; DATA XREF: _configure_timer+1Bw"),('0, // audio_len\n','dw audio_len;\n', 2))
        self.assertEqual(parser_instance.action_data(line="b dw 2"),('2, // b\n','dw b;\n', 2))
        self.assertEqual(parser_instance.action_data(line="beginningdata db 4"),('4, // beginningdata\n','db beginningdata;\n', 1))
        self.assertEqual(parser_instance.action_data(line="cc db 3"),('3, // cc\n','db cc;\n', 1))
        self.assertEqual(parser_instance.action_data(line="d db 4"),('4, // d\n','db d;\n', 1))
        self.assertEqual(parser_instance.action_data(line="db    0"),('0, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db    ?	;"),('0, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db  0Ah"),('10, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db  20h"),('32, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db  20h"),('32, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db  2Ch	; ,"),('44, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db  80h	; Ç"),('128, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db  8Ah	; è"),('138, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db ' '"),("{' '}, // dummy1\n",'char dummy1[1];\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db ' /?  This help screen',0Dh,0Ah"),("{' ','/','?',' ',' ','T','h','i','s',' ','h','e','l','p',' ','s','c','r','e','e','n','\\r','\\n'}, // dummy1\n",'char dummy1[23];\n', 23))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db ','"),("{','}, // dummy1\n",'char dummy1[1];\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db '- +'"),("{'-',' ','+'}, // dummy1\n",'char dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db ':'"),("{':'}, // dummy1\n",'char dummy1[1];\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'ABC',0"),('"ABC", // dummy1\n','char dummy1[4];\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'Close this DOS session first with the \"EXIT\" command.',0Dh,0Ah"),("{'C','l','o','s','e',' ','t','h','i','s',' ','D','O','S',' ','s','e','s','s','i','o','n',' ','f','i','r','s','t',' ','w','i','t','h',' ','t','h','e',' ','\\\"','E','X','I','T','\\\"',' ','c','o','m','m','a','n','d','.','\\r','\\n'}, // dummy1\n",'char dummy1[55];\n', 55))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'OKOKOKOK'"),("{'O','K','O','K','O','K','O','K'}, // dummy1\n",'char dummy1[8];\n', 8))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'OKOKOKOK',10,13"),("{'O','K','O','K','O','K','O','K','\\n','\\r'}, // dummy1\n",'char dummy1[10];\n', 10))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'Try changing the AT-BUS Clock in the CMOS Setup.',0Dh,0Ah,0"),('"Try changing the AT-BUS Clock in the CMOS Setup.\\r\\n", // dummy1\n','char dummy1[51];\n', 51))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'Usage: IPLAY [Switches] [FileName.Ext|@FileList.Ext]',0Dh,0Ah"),("{'U','s','a','g','e',':',' ','I','P','L','A','Y',' ','[','S','w','i','t','c','h','e','s',']',' ','[','F','i','l','e','N','a','m','e','.','E','x','t','|','@','F','i','l','e','L','i','s','t','.','E','x','t',']','\\r','\\n'}, // dummy1\n",'char dummy1[54];\n', 54))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db '[ ]'"),("{'[',' ',']'}, // dummy1\n",'char dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db '[ ]',0"),('"[ ]", // dummy1\n','char dummy1[4];\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'ed again.',0Dh,0Ah"),("{'e','d',' ','a','g','a','i','n','.','\\r','\\n'}, // dummy1\n",'char dummy1[11];\n', 11))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'h'"),("{'h'}, // dummy1\n",'char dummy1[1];\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 'o:'"),("{'o',':'}, // dummy1\n",'char dummy1[2];\n', 2))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 's'"),("{'s'}, // dummy1\n",'char dummy1[1];\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 's',0Dh,0Ah,0"),('"s\\r\\n", // dummy1\n','char dummy1[4];\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db '─asdkweorjwoerj3434',13,10,92"),("{'\\xc4','a','s','d','k','w','e','o','r','j','w','o','e','r','j','3','4','3','4','\\r','\\n',92}, // dummy1\n",'char dummy1[22];\n', 22))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0"),('0, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0,2Ah,2Ah"),('{0,42,42}, // dummy1\n','db dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0A0h	; á		; self modifying"),('160, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0A0h	; á"),('160, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0A0h,0A4h,0A8h,0ACh,0B0h,0B4h,0B8h,0BCh,0C0h,0C4h,0C8h"),('{160,164,168,172,176,180,184,188,192,196,200}, // dummy1\n','db dummy1[11];\n', 11))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0A1h"),('161, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0A1h,0A5h,0AAh,0AEh,0B2h,0B6h,0BAh,0BEh,0C2h,0C6h,0CAh"),('{161,165,170,174,178,182,186,190,194,198,202}, // dummy1\n','db dummy1[11];\n', 11))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0AAh	; ¬"),('170, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0Ah"),('10, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0Ah,'$'"),("{'\\n','$'}, // dummy1\n",'char dummy1[2];\n', 2))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0Ah,0Bh,1Bh"),('{10,11,27}, // dummy1\n','db dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0B8h,0BBh,0BEh,0C1h,0C3h,0C6h,0C9h,0CCh,0CFh,0D1h,0D4h"),('{184,187,190,193,195,198,201,204,207,209,212}, // dummy1\n','db dummy1[11];\n', 11))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0C5h,0B4h,0A1h,8Dh,78h,61h,4Ah,31h,18h"),('{197,180,161,141,120,97,74,49,24}, // dummy1\n','db dummy1[9];\n', 9))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0Dh,0Ah"),('{13,10}, // dummy1\n','db dummy1[2];\n', 2))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 0Dh,0Ah,'$'"),("{'\\r','\\n','$'}, // dummy1\n",'char dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 1"),('1, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 1,1,1,1,1"),('{1,1,1,1,1}, // dummy1\n','db dummy1[5];\n', 5))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 1,2,3,4"),('{1,2,3,4}, // dummy1\n','db dummy1[4];\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 10h,11h,2Ah"),('{16,17,42}, // dummy1\n','db dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 12"),('12, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 141"),('141, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 7Fh"),('127, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 8,8,8,7,7,7,7,6,6,6,6,6,6,5,5,5"),('{8,8,8,7,7,7,7,6,6,6,6,6,6,5,5,5}, // dummy1\n','db dummy1[16];\n', 16))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 80h"),('128, // dummy1\n','db dummy1;\n', 1))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 9,9,8"),('{9,9,8}, // dummy1\n','db dummy1[3];\n', 3))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dd   -2,  -1,  -1,  -1,	 -1,   0"),('{4294967294,4294967295,4294967295,4294967295,4294967295,0}, // dummy1\n','dd dummy1[6];\n', 24))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dd  201, 100,  50,  25,	 12"),('{201,100,50,25,12}, // dummy1\n','dd dummy1[5];\n', 20))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dd 111,1"),('{111,1}, // dummy1\n','dd dummy1[2];\n', 8))
        parser_instance = Parser([])
        #self.assertEqual(parser_instance.action_data(line="dd offset var5"),('offset(_data,var5), // dummy1\n','dw dummy1;\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dd unk_24453"),('0, // dummy1\n','dd dummy1;\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="doublequote db 'ab''cd',\"e\""),("{'a','b','\\'','\\'','c','d','e'}, // doublequote\n",'char doublequote[7];\n', 7))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dw  0, 0, 0, 0,	0, 0, 0, 0, 0, 0, 0, 0,	0, 0, 0, 0"),('{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, // dummy1\n','dw dummy1[16];\n', 32))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dw  5,5622h, 7,6B25h, 4,7D00h, 6,8133h,0Dh,93A8h, 9,0AC44h"),('{5,22050,7,27429,4,32000,6,33075,13,37800,9,44100}, // dummy1\n','dw dummy1[12];\n', 24))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dw 0A06h"),('2566, // dummy1\n','dw dummy1;\n', 2))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dw 0BE0h,0B40h,0AA0h,0A00h,970h,8F0h,870h,7F0h,780h,710h"),('{3040,2880,2720,2560,2416,2288,2160,2032,1920,1808}, // dummy1\n','dw dummy1[10];\n', 20))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dw 0Bh,0BB80h,0Ch"),('{11,48000,12}, // dummy1\n','dw dummy1[3];\n', 6))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="dw 32Ah"),('810, // dummy1\n','dw dummy1;\n', 2))
        parser_instance = Parser([])
        #self.assertEqual(parser_instance.action_data(line="dw @df@@@@8"),('karbdfarbarbarbarb8, // dummy1\n','dw dummy1;\n', 2))
        parser_instance = Parser([])
        #self.assertEqual(parser_instance.action_data(line="dw offset __2stm_module	; 2STM"),('k__2stm_module, // dummy1\n','dw dummy1;\n', 2))
        parser_instance = Parser([])
        #self.assertEqual(parser_instance.action_data(line="dw offset loc_17BEB"),('kloc_17beb, // dummy1\n','dw dummy1;\n', 2))
        self.assertEqual(parser_instance.action_data(line="e db 5"),('5, // e\n','db e;\n', 1))
        self.assertEqual(parser_instance.action_data(line="enddata db 4"),('4, // enddata\n','db enddata;\n', 1))
        self.assertEqual(parser_instance.action_data(line="f db 6"),('6, // f\n','db f;\n', 1))
        self.assertEqual(parser_instance.action_data(line="fileName db 'file1.txt',0"),('"file1.txt", // filename\n','char filename[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="g dd 12345"),('12345, // g\n','dd g;\n', 4))
        self.assertEqual(parser_instance.action_data(line="h db -1"),('255, // h\n','db h;\n', 1))
        self.assertEqual(parser_instance.action_data(line="h2 db 1"),('1, // h2\n','db h2;\n', 1))
        self.assertEqual(parser_instance.action_data(line="load_handle dd 0"),('0, // load_handle\n','dd load_handle;\n', 4))
        self.assertEqual(parser_instance.action_data(line="myoffs		dw offset label2"),('0, // myoffs\n','dw myoffs;\n', 2))
        #self.assertEqual(parser_instance.action_data(line="off_18E00	dw offset loc_16A89	; DATA XREF: sub_1609F:loc_16963r"),('kloc_16a89, // off_18e00\n','dw off_18e00;\n', 2))
        #self.assertEqual(parser_instance.action_data(line="off_25326	dw offset _inr_module	; DATA XREF: _moduleread:loc_10040o"),('k_inr_module, // off_25326\n','dw off_25326;\n', 2))
        self.assertEqual(parser_instance.action_data(line="pal_jeu db 000,000,000,000,000,021,000,000,042,000,000,063,009,000,000,009"),('{0,0,0,0,0,21,0,0,42,0,0,63,9,0,0,9}, // pal_jeu\n','db pal_jeu[16];\n', 16))
        self.assertEqual(parser_instance.action_data(line="pas_de_mem  db 'NOT enought memory for VGA display, controls work for network games',13,10,'$'"),("{'N','O','T',' ','e','n','o','u','g','h','t',' ','m','e','m','o','r','y',' ','f','o','r',' ','V','G','A',' ','d','i','s','p','l','a','y',',',' ','c','o','n','t','r','o','l','s',' ','w','o','r','k',' ','f','o','r',' ','n','e','t','w','o','r','k',' ','g','a','m','e','s','\\r','\\n','$'}, // pas_de_mem\n",'char pas_de_mem[70];\n', 70))
        self.assertEqual(parser_instance.action_data(line="pbs1        db 'probleme dans allocation de descriptor..',13,10,'$'"),("{'p','r','o','b','l','e','m','e',' ','d','a','n','s',' ','a','l','l','o','c','a','t','i','o','n',' ','d','e',' ','d','e','s','c','r','i','p','t','o','r','.','.','\\r','\\n','$'}, // pbs1\n",'char pbs1[43];\n', 43))
        self.assertEqual(parser_instance.action_data(line="pbs2        db 'probleme dans dans definition de la taille du segment',13,10,'$'"),("{'p','r','o','b','l','e','m','e',' ','d','a','n','s',' ','d','a','n','s',' ','d','e','f','i','n','i','t','i','o','n',' ','d','e',' ','l','a',' ','t','a','i','l','l','e',' ','d','u',' ','s','e','g','m','e','n','t','\\r','\\n','$'}, // pbs2\n",'char pbs2[56];\n', 56))
        self.assertEqual(parser_instance.action_data(line="str1 db 'abcde'"),("{'a','b','c','d','e'}, // str1\n",'char str1[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="str2 db 'abcde'"),("{'a','b','c','d','e'}, // str2\n",'char str2[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="str3 db 'cdeab'"),("{'c','d','e','a','b'}, // str3\n",'char str3[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="table   dw 0"),('0, // table\n','dw table;\n', 2))
        self.assertEqual(parser_instance.action_data(line="testOVerlap db 1,2,3,4,5,6,7,8,9,10,11,12,13,14"),('{1,2,3,4,5,6,7,8,9,10,11,12,13,14}, // testoverlap\n','db testoverlap[14];\n', 14))
        self.assertEqual(parser_instance.action_data(line="unk_16464	db    0			; DATA XREF: sub_1609F+235w"),('0, // unk_16464\n','db unk_16464;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_165AD	db    0			; DATA XREF: sub_1609F+251w"),('0, // unk_165ad\n','db unk_165ad;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_1D516	db    2"),('2, // unk_1d516\n','db unk_1d516;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_1D6C3	db    2			; DATA XREF: seg001:1BDAo"),('2, // unk_1d6c3\n','db unk_1d6c3;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_1DC01	db    0			; DATA XREF: _modules_search+8Fr"),('0, // unk_1dc01\n','db unk_1dc01;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_1DC70	db    0			; DATA XREF: _modules_search+1D8o"),('0, // unk_1dc70\n','db unk_1dc70;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_1DC7B	db    0			; DATA XREF: _modules_search+1C9o"),('0, // unk_1dc7b\n','db unk_1dc7b;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_23EE4	db    0			; DATA XREF: _init_f5_spectr+98o"),('0, // unk_23ee4\n','db unk_23ee4;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_24074	db    0			; DATA XREF: _f5_draw_spectr+5A9o"),('0, // unk_24074\n','db unk_24074;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_24453	db    0			; DATA XREF: dseg:7C57o"),('0, // unk_24453\n','db unk_24453;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_24456	db  20h			; DATA XREF: dseg:7C5Bo dseg:7C5Fo"),('32, // unk_24456\n','db unk_24456;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_244C4	db    0			; DATA XREF: _spectr_1B084+14Ew"),('0, // unk_244c4\n','db unk_244c4;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_257D9	db    0"),('0, // unk_257d9\n','db unk_257d9;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_258A6	db  49h	; I		; DATA XREF: _useless_writeinr_118+Eo"),('73, // unk_258a6\n','db unk_258a6;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_30528	db    ?	;		; DATA XREF: _s3m_module+102r"),('0, // unk_30528\n','db unk_30528;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_3054A	db    ?	;		; DATA XREF: _mtm_module+7Bo"),('0, // unk_3054a\n','db unk_3054a;\n', 1))
        self.assertEqual(parser_instance.action_data(line="unk_30941	db    ?	;		; DATA XREF: _mod_n_t_module+ACr"),('0, // unk_30941\n','db unk_30941;\n', 1))
        self.assertEqual(parser_instance.action_data(line="var db 4 dup (5)"),('{5,5,5,5}, // var\n','db var[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="var0 db 10 dup (?)"),('{0,0,0,0,0,0,0,0,0,0}, // var0\n','db var0[10];\n', 10))
        self.assertEqual(parser_instance.action_data(line="var1 db 1,2,3"),('{1,2,3}, // var1\n','db var1[3];\n', 3))
        self.assertEqual(parser_instance.action_data(line="var2 db 5 dup (0)"),('{0,0,0,0,0}, // var2\n','db var2[5];\n', 5))
        self.assertEqual(parser_instance.action_data(line="var3 db 5*5 dup (0,testEqu*2,2*2,3)"),('{0,0,4,0}, // var3\n','db var3[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="var4 db 131"),('131, // var4\n','db var4;\n', 1))
        self.assertEqual(parser_instance.action_data(line="var5 db 'abcd'"),("{'a','b','c','d'}, // var5\n",'char var5[4];\n', 4))
        self.assertEqual(parser_instance.action_data(line="var6 dd 9,8,7,1"),('{9,8,7,1}, // var6\n','dd var6[4];\n', 16))
        self.assertEqual(parser_instance.action_data(line="var7 db 5*5 dup (0,testEqu*2,2*2,3)"),('{0,0,4,0}, // var7\n','db var7[4];\n', 4))
        parser_instance = Parser([])
        self.assertEqual(parser_instance.action_data(line="db 000,009,000,000,009,021,000,009,042,000,009,063,009,009,000,009"),('{0,9,0,0,9,21,0,9,42,0,9,63,9,9,0,9}, // dummy1\n','db dummy1[16];\n', 16))

if __name__ == "__main__":
    unittest.main()
