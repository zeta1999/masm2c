# ScummVM - Graphic Adventure Engine
#
# ScummVM is the legal property of its developers, whose names
# are too numerous to list here. Please refer to the COPYRIGHT
# file distributed with this source distribution.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import op, traceback, re, proc, string
from copy import copy
proc_module = proc

class CrossJump(Exception):
	pass

def parse_bin(s):
	b = s.group(1)
	v = hex(int(b, 2))
	#print "BINARY: %s -> %s" %(b, v)
	return v

class cpp:
	def __init__(self, context, namespace, skip_first = 0, blacklist = [], skip_output = [], skip_dispatch_call = False, skip_addr_constants = False, header_omit_blacklisted = False, function_name_remapping = { }):
		self.namespace = namespace
		fname = namespace.lower() + ".cpp"
		header = namespace.lower() + ".h"
		banner = """/* PLEASE DO NOT MODIFY THIS FILE. ALL CHANGES WILL BE LOST! LOOK FOR README FOR DETAILS */

/* ScummVM - Graphic Adventure Engine
 *
 * ScummVM is the legal property of its developers, whose names
 * are too numerous to list here. Please refer to the COPYRIGHT
 * file distributed with this source distribution.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 */
"""
		self.fd = open(fname, "wt")
		self.hd = open(header, "wt")
		hid = "TASMRECOVER_%s_STUBS_H__" %namespace.upper()
		self.hd.write("""#ifndef %s
#define %s

%s""" %(hid, hid, banner))
		self.context = context
		self.data_seg = context.binary_data
		self.cdata_seg = context.c_data
		self.hdata_seg = context.h_data
		self.procs = context.proc_list
		self.skip_first = skip_first
		self.proc_queue = []
		self.proc_done = []
		self.blacklist = blacklist
		self.failed = list(blacklist)
		self.skip_output = skip_output
		self.skip_dispatch_call = skip_dispatch_call
		self.skip_addr_constants = skip_addr_constants
		self.header_omit_blacklisted = header_omit_blacklisted
		self.function_name_remapping = function_name_remapping
		self.translated = []
		self.proc_addr = []
		self.used_data_offsets = set()
		self.methods = []
		self.pointer_flag = False
		self.fd.write("""%s
#include "asm.c"
#include \"%s\"

void _start();

int main()
{
	_start();
	return(0);
}
//namespace %s {
""" %(banner, header, namespace))
		self.expr_size = 0

	def expand_cb(self, match):
		name = match.group(0).lower()
		print "expand_cb name = %s indirection = %u" %(name, self.indirection)
		if len(name) == 2 and \
			((name[0] in ['a', 'b', 'c', 'd'] and name[1] in ['h', 'x', 'l']) or name in ['si', 'di', 'bp', 'es', 'ds', 'cs', 'fs', 'gs']):
			return "%s" %name

		if len(name) == 3 and \
			(name in ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp']):
			return "%s" %name

		if self.indirection == -1:
			try:
				offset,p,p = self.context.get_offset(name)
			except:
				pass
			else:
				print "OFFSET = %s" %offset
				self.indirection = 0
				self.used_data_offsets.add((name,offset))
				return "offset_%s" % (name,)

		try:
			g = self.context.get_global(name)
		except:
			print "expand_cb exception on name = %s" %name
			return ""
			
		if isinstance(g, op.const):
			value = self.expand_equ(g.value)
			print "equ: %s -> %s" %(name, value)
		elif isinstance(g, proc.proc):
			if self.indirection != -1:
				print "proc %s offset %s" %(str(proc.proc), str(g.offset))
				raise Exception("invalid proc label usage")
			value = str(g.offset)
			self.indirection = 0
		else:
			size = g.size
			if size == 0:
				raise Exception("invalid var '%s' size %u" %(name, size))
			if self.indirection == 0 or self.indirection == 1: # x0r self.indirection == 1 ??
				if (self.expr_size != 0 and self.expr_size != size) or g.elements > 1:
					self.pointer_flag = True
					value = "(db*)&m.%s" %(name)
					print "value %s" %value
				else:
					value = "m." + name
				if self.indirection == 1:
					self.indirection = 0
			elif self.indirection == -1:
				value = "%s" %g.offset
				self.indirection = 0
			else:
				raise Exception("invalid indirection %d name '%s' size %u" %(self.indirection, name, size))
		return value

	def get_size(self, expr):
		expr = expr.strip()
		print 'get_size("%s")' %expr
		try:
			v = self.context.parse_int(expr)
			size = 0
			if v < 0:
				raise Exception("negative not handled yet")
			elif v < 256:
				size = 1
			elif v < 65536:
				size = 2
			elif v < 4294967296:
				size = 4
			print 'get_size res %d' %size
			return size
		except:
			pass

		if re.match(r'byte\s+ptr\s', expr) is not None:
			print 'get_size res 1'
			return 1

		if re.match(r'word\s+ptr\s', expr) is not None:
			print 'get_size res 2'
			return 2

		if re.match(r'dword\s+ptr\s', expr) is not None:
			print 'get_size res 4'
			return 4

		if len(expr) == 2 and expr[0] in ['a', 'b', 'c', 'd'] and expr[1] in ['h', 'l']:
			print 'get_size res 1'
			return 1
		if expr in ['ax', 'bx', 'cx', 'dx', 'si', 'di', 'sp', 'bp', 'ds', 'cs', 'es', 'fs', 'gs']:
			print 'get_size res 2'
			return 2
		if expr in ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'ebp']:
			print 'get_size res 4'
			return 4

		m = re.match(r'\[([a-zA-Z_]\w*)\]', expr)
		if m is not None:
			expr = m.group(1).strip()

		m = re.match(r'[a-zA-Z_]\w*', expr)
		if m is not None:
			print 'expr match some a-z'
			name = m.group(0)
			print 'name = %s' %name
			try:
				g = self.context.get_global(name)
				print 'get_size res %d' %g.size
				return g.size
			except:
				pass

		print 'get_size res 0'
		return 0

	def expand_equ_cb(self, match):
		name = match.group(0).lower()
		g = self.context.get_global(name)
		if isinstance(g, op.const):
			return g.value
		return str(g.offset)

	def expand_equ(self, expr):
		n = 1
		while n > 0:
			expr, n = re.subn(r'\b[a-zA-Z_][a-zA-Z0-9_]+\b', self.expand_equ_cb, expr)
		expr = re.sub(r'\b([0-9][a-fA-F0-9]*)h', '0x\\1', expr)
		return "(%s)" %expr

	def expand(self, expr, def_size = 0):
		print "EXPAND \"%s\"" %expr

		expr = expr.strip()

		size = self.get_size(expr) if def_size == 0 else def_size
		self.expr_size = size
		#print "expr \"%s\" %d" %(expr, size)
		indirection = 0
		seg = None
		reg = True

		ex = string.replace(expr, "\\\\", "\\")
		m = re.match(r'\'(..+)\'$', ex)
		if m is not None:
			s = ""
			for c in m.group(1):
				s = '{:02X}'.format(ord(c)) + s
			expr = "0x" + s

		m = re.match(r'seg\s+(.*?)$', expr)
		if m is not None:
			return "data"

		match_id = True
		#print "is it offset ~%s~" %expr
		m = re.match(r'offset\s+(.*?)$', expr)
		if m is not None:
			indirection -= 1
			expr = m.group(1).strip()
		#print "after is it offset ~%s~" %expr

		m = re.match(r'byte\s+ptr\s+(.*?)$', expr)
		if m is not None:
			expr = m.group(1).strip()

		m = re.match(r'word\s+ptr\s+(.*?)$', expr)
		if m is not None:
			expr = m.group(1).strip()

		m = re.match(r'dword\s+ptr\s+(.*?)$', expr)
		if m is not None:
			expr = m.group(1).strip()

		m = re.match(r'\[(.*)\]$', expr)
		if m is not None:
			indirection += 1
			expr = m.group(1).strip()

		m = re.match(r'(\w{2,2}):(.*)$', expr)
		if m is not None:
			seg_prefix = m.group(1)
			expr = m.group(2).strip()
			print "SEGMENT %s, remains: %s" %(seg_prefix, expr)
		else:
			seg_prefix = "ds"

		m = re.match(r'((e?[abcd][xhl])|si|di|bp|sp)([\+-].*)?$', expr)
		if m is not None:
			reg = m.group(1)
			plus = m.group(3)
			if plus is not None:
				plus = self.expand(plus)
			else:
				plus = ""
			match_id = False
			#print "COMMON_REG: ", reg, plus
			expr = "%s%s" %(reg, plus)

		expr = re.sub(r'\b([0-9][a-fA-F0-9]*)h', '0x\\1', expr)
		expr = re.sub(r'\b([0-1]+)b', parse_bin, expr)
		expr = re.sub(r'"(.)"', '\'\\1\'', expr)
		if match_id:
			print "BEFORE: %d %s" %(indirection, expr)
			self.indirection = indirection
			self.pointer_flag = False
			expr = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]+\b', self.expand_cb, expr)
			print "AFTER: %d %s" %(self.indirection, expr)
			print "is a pointer %d expr_size %d" %(self.pointer_flag, self.expr_size)
			if self.pointer_flag:
				if self.expr_size == 1:  # x0r
					expr = "*(db*)(%s)" %(expr)
				elif self.expr_size == 2:
					expr = "*(dw*)(%s)" %(expr)
				elif self.expr_size == 4:
					expr = "*(dd*)(%s)" %(expr)

			self.pointer_flag = False
			indirection = self.indirection
			print "AFTER: %d %s" %(indirection, expr)

		if indirection == 1:
			if size == 1:
				expr = "*(db*)(raddr(%s,%s))" %(seg_prefix, expr)
			elif size == 2:
				expr = "*(dw*)(raddr(%s,%s))" %(seg_prefix, expr)
			elif size == 4:
				expr = "*(dd*)(raddr(%s,%s))" %(seg_prefix, expr)
			else:
				expr = "@invalid size 0"
			print "expr: %s" %expr
		elif indirection == 0:
			pass
		elif indirection == -1:
			expr = "&%s" %expr
		else:
			raise Exception("invalid indirection %d" %indirection)
		return expr

	def extract_brackets(self, expr):
		expr = expr.strip()
		print "extract_brackets %s" %expr
		m = re.match(r'\[(.*)\]$', expr)
		if m is not None:
			#indirection += 1
			expr = m.group(1).strip()
		print "extract_brackets res: %s" %expr
		return expr

	def mangle_label(self, name):
		name = name.lower()
		return re.sub(r'\$', '_tmp', name)

	def resolve_label(self, name):
		name = name.lower()
		if not name in self.proc.labels:
			try:
				offset, proc, pos = self.context.get_offset(name)
			except:
				print "no label %s, trying procedure" %name
				try:
					proc = self.context.get_global(name)
				except:
					print "resolve_label exception"
					return name

				pos = 0
				if not isinstance(proc, proc_module.proc):
					raise CrossJump("cross-procedure jump to non label and non procedure %s" %(name))
			self.proc.labels.add(name)
			for i in xrange(0, len(self.unbounded)):
				u = self.unbounded[i]
				if u[1] == proc:
					if pos < u[2]:
						self.unbounded[i] = (name, proc, pos)
				return self.mangle_label(name)
			self.unbounded.append((name, proc, pos))

		return self.mangle_label(name)

	def jump_to_label(self, name):
		jump_proc = False
		if name in self.blacklist:
			jump_proc = True

		if self.context.has_global(name) :
			g = self.context.get_global(name)
			if isinstance(g, proc_module.proc):
				jump_proc = True

		if jump_proc:
			if name in self.function_name_remapping:
				return "{ %s(); return; }" %self.function_name_remapping[name]
			else:
				return "{ %s(); return; }" %name
		else:
			# TODO: name or self.resolve_label(name) or self.mangle_label(name)??
			if name in self.proc.retlabels:
				return "return /* (%s) */" % (name)
			# x0r return "goto %s" %self.resolve_label(name)
			return "%s" %self.resolve_label(name)

	def _label(self, name):
		self.body += "%s:\n" %self.mangle_label(name)

	def schedule(self, name):
		name = name.lower()
		if name in self.proc_queue or name in self.proc_done or name in self.failed:
			return
		print "+scheduling function %s..." %name
		self.proc_queue.append(name)

	def _call(self, name):
		name = name.lower()
		if name == 'ax':
			self.body += "\t__dispatch_call(%s);\n" %self.expand('ax', 2)
			return
		if name in self.function_name_remapping:
			self.body += "\t%s();\n" %self.function_name_remapping[name]
		else:
			self.body += "\t%s();\n" %name
		self.schedule(name)

	def _ret(self):
		self.body += "\tR(return);\n"

	def parse2(self, dst, src):
		dst_size, src_size = self.get_size(dst), self.get_size(src)
		if dst_size == 0:
			if src_size == 0:
				print "parse2: %s  %s" %(dst, src)
				raise Exception("both sizes are 0")
			dst_size = src_size
		if src_size == 0:
			src_size = dst_size

		dst = self.expand(dst, dst_size)
		src = self.expand(src, src_size)
		return dst, src

	def _mov(self, dst, src):
		self.body += "\tR(MOV(%s, %s));\n" %self.parse2(dst, src)

	def _add(self, dst, src):
		self.body += "\tR(ADD(%s, %s));\n" %self.parse2(dst, src)

	def _sub(self, dst, src):
		self.d, self.s = self.parse2(dst, src)
		if self.d == self.s:
			self.body += "\t%s = 0;\n" %self.d
		else:
			self.body += "\tR(SUB(%s, %s));\n" %(self.d, self.s)

	def _and(self, dst, src):
		self.body += "\tR(AND(%s, %s));\n" %self.parse2(dst, src)

	def _or(self, dst, src):
		self.body += "\tR(OR(%s, %s));\n" %self.parse2(dst, src)

	def _xor(self, dst, src):
		self.d, self.s = self.parse2(dst, src)
		if self.d == self.s:
			self.body += "\t%s = 0;\n" %self.d
		else:
			self.body += "\tR(XOR(%s, %s));\n" %(self.d, self.s)

	def _neg(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(NEG(%s));\n" %(dst)

	def _cbw(self):
		self.body += "\tR(CBW());\n"

	def _shr(self, dst, src):
		self.body += "\tR(SHR(%s, %s));\n" %self.parse2(dst, src)

	def _shl(self, dst, src):
		self.body += "\tR(SHL(%s, %s));\n" %self.parse2(dst, src)

	def _sar(self, dst, src):
		self.body += "\tR(SAR(%s%s));\n" %self.parse2(dst, src)

	def _sal(self, dst, src):
		self.body += "\tR(SAL(%s, %s));\n" %self.parse2(dst, src)

	def _rcl(self, dst, src):
		self.body += "\tR(RCL(%s, %s));\n" %self.parse2(dst, src)

	def _rcr(self, dst, src):
		self.body += "\tR(RCR(%s, %s));\n" %self.parse2(dst, src)

	def _mul(self, src):
		src = self.expand(src)
		self.body += "\tR(MUL(%s));\n" %(src)

	def _imul(self, src):
		src = self.expand(src)
		self.body += "\tR(IMUL(%s));\n" %(src)

	def _div(self, src):
		src = self.expand(src)
		self.body += "\tR(DIV(%s));\n" %(src)

	def _idiv(self, src):
		src = self.expand(src)
		self.body += "\tR(IDIV(%s));\n" %(src)

	def _inc(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(INC(%s));\n" %(dst)

	def _dec(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(DEC(%s));\n" %(dst)

	def _cmp(self, a, b):
		self.body += "\tR(CMP(%s, %s));\n" %self.parse2(a, b)

	def _test(self, a, b):
		self.body += "\tR(TEST(%s, %s));\n" %self.parse2(a, b)

	def _js(self, label):
		self.body += "\t\tR(JS(%s));\n" %(self.jump_to_label(label))

	def _jns(self, label):
		self.body += "\t\tR(JNS(%s));\n" %(self.jump_to_label(label))

	def _jz(self, label):
		self.body += "\t\tR(JZ(%s));\n" %(self.jump_to_label(label))

	def _jnz(self, label):
		self.body += "\t\tR(JNZ(%s));\n" %(self.jump_to_label(label))

	def _jl(self, label):
		self.body += "\t\tR(JL(%s));\n" %(self.jump_to_label(label))

	def _jg(self, label):
		self.body += "\t\tR(JG(%s));\n" %(self.jump_to_label(label))

	def _jle(self, label):
		self.body += "\t\tR(JLE(%s));\n" %(self.jump_to_label(label))

	def _jge(self, label):
		self.body += "\t\tR(JGE(%s));\n" %(self.jump_to_label(label))

	def _jbe(self, label):
		self.body += "\t\tR(JBE(%s));\n" %(self.jump_to_label(label))

	def _ja(self, label):
		self.body += "\t\tR(JA(%s));\n" %(self.jump_to_label(label))

	def _jc(self, label):
		self.body += "\t\tR(JC(%s));\n" %(self.jump_to_label(label))

	def _jb(self, label):
		self.body += "\t\tR(JB(%s));\n" %(self.jump_to_label(label))

	def _jnc(self, label):
		self.body += "\t\tR(JNC(%s));\n" %(self.jump_to_label(label))

	def _xchg(self, dst, src):
		self.body += "\tR(XCHG(%s, %s));\n" %self.parse2(dst, src)

	def _jmp(self, label):
		self.body += "\t\tR(JMP(%s));\n" %(self.jump_to_label(label))

	def _loop(self, label):
		self.body += "\t\tR(LOOP(%s));\n" %self.jump_to_label(label)

	def _jcxz(self, label):
		self.body += "\t\tR(JCXZ(%s));\n" %(self.jump_to_label(label))

	def _push(self, regs):
		p = str();
		for r in regs:
			r = self.expand(r)
			p += "\tPUSH(%s);\n" %(r)
		self.body += p

	def _pop(self, regs):
		p = str();
		for r in regs:
			self.temps_count -= 1
			i = self.temps_count
			r = self.expand(r)
			p += "\tPOP(%s);\n" %r
		self.body += p

	def _rep(self):
		self.body += "\tREP_"

	def _lodsb(self):
		self.body += "LODSB();\n"

	def _lodsw(self):
		self.body += "LODSW();\n"

	def _stosb(self, n, clear_cx):
		self.body += "STOSB(%s%s);\n" %("" if n == 1 else n, ", true" if clear_cx else "")

	def _stosw(self, n, clear_cx):
		self.body += "STOSW(%s%s);\n" %("" if n == 1 else n, ", true" if clear_cx else "")

	def _stosd(self, n, clear_cx):
		self.body += "STOSD(%s%s);\n" %("" if n == 1 else n, ", true" if clear_cx else "")

	def _movsb(self, n, clear_cx):
		self.body += "MOVSB(%s%s);\n" %("" if n == 1 else n, ", true" if clear_cx else "")

	def _movsw(self, n, clear_cx):
		self.body += "MOVSW(%s%s);\n" %("" if n == 1 else n, ", true" if clear_cx else "")

	def _movsd(self, n, clear_cx):
		self.body += "MOVSD(%s%s);\n" %("" if n == 1 else n, ", true" if clear_cx else "")

	def _stc(self):
		self.body += "\tR(STC);\n"

	def _clc(self):
		self.body += "\tR(CLC);\n"

	def _cld(self):
		self.body += "\tR(CLD);\n"

	def _std(self):
		self.body += "\tR(STD);\n"

	def _cmc(self):
		self.body += "\tR(CMC);\n"

	def __proc(self, name, def_skip = 0):
		try:
			skip = def_skip
			self.temps_count = 0
			self.temps_max = 0
			if self.context.has_global(name):
				self.proc = self.context.get_global(name)
			else:
				print "No procedure named %s, trying label" %name
				off, src_proc, skip = self.context.get_offset(name)

				self.proc = proc_module.proc(name)
				self.proc.stmts = copy(src_proc.stmts)
				self.proc.labels = copy(src_proc.labels)
				self.proc.retlabels = copy(src_proc.retlabels)
				#for p in xrange(skip, len(self.proc.stmts)):
				#	s = self.proc.stmts[p]
				#	if isinstance(s, op.basejmp):
				#		o, p, s = self.context.get_offset(s.label)
				#		if p == src_proc and s < skip:
				#			skip = s


			self.proc_addr.append((name, self.proc.offset))
			self.body = str()
			'''
			if name in self.function_name_remapping:
				self.body += "void %sContext::%s() {\n" %(self.namespace, self.function_name_remapping[name]);
			else:
				self.body += "void %sContext::%s() {\n" %(self.namespace, name);
			'''
			if name in self.function_name_remapping:
				self.body += "void %s() {\n" %(self.function_name_remapping[name]);
			else:
				self.body += "void %s() {\n" %(name);

			print name
			self.proc.optimize()
			self.unbounded = []
			self.proc.visit(self, skip)

			#adding remaining labels:
			for i in xrange(0, len(self.unbounded)):
				u = self.unbounded[i]
				print "UNBOUNDED: ", u
				proc = u[1]
				for p in xrange(u[2], len(proc.stmts)):
					s = proc.stmts[p]
					if isinstance(s, op.basejmp):
						self.resolve_label(s.label)

			#adding statements
			#BIG FIXME: this is quite ugly to handle code analysis from the code generation. rewrite me!
			for label, proc, offset in self.unbounded:
				self.body += "\tR(return);\n" #we need to return before calling code from the other proc
				self.body += "/*continuing to unbounded code: %s from %s:%d-%d*/\n" %(label, proc.name, offset, len(proc.stmts))
				start = len(self.proc.stmts)
				self.proc.add_label(label)
				for s in proc.stmts[offset:]:
					if isinstance(s, op.label):
						self.proc.labels.add(s.name)
					self.proc.stmts.append(s)
				self.proc.add("ret")
				print "skipping %d instructions, todo: %d" %(start, len(self.proc.stmts) - start)
				print "re-optimizing..."
				self.proc.optimize(keep_labels=[label])
				self.proc.visit(self, start)
			self.body += "}\n";
			if name not in self.skip_output:
				self.translated.insert(0, self.body)
			self.proc = None
			if self.temps_count > 0:
				raise Exception("temps count == %d at the exit of proc" %self.temps_count);
			return True
		except (CrossJump, op.Unsupported) as e:
			print "%s: ERROR: %s" %(name, e)
			self.failed.append(name)
		except:
			raise

	def get_type(self, width):
		return "uint%d_t" %(width * 8)

	def write_stubs(self, fname, procs):
		fd = open(fname, "wt")
		fd.write("//namespace %s {\n" %self.namespace)
		for p in procs:
			if p in self.function_name_remapping:
				fd.write("void %sContext::%s() {\n\t::error(\"%s\");\n}\n\n" %(self.namespace, self.function_name_remapping[p], self.function_name_remapping[p]))
			else:
				fd.write("void %sContext::%s() {\n\t::error(\"%s\");\n}\n\n" %(self.namespace, p, p))
		fd.write("//} // End of namespace  %s\n" %self.namespace)
		fd.close()


	def generate(self, start):
		#print self.prologue()
		#print context
		self.proc_queue.append(start)
		while len(self.proc_queue):
			name = self.proc_queue.pop()
			if name in self.failed or name in self.proc_done:
				continue
			if len(self.proc_queue) == 0 and len(self.procs) > 0:
				print "queue's empty, adding remaining procs:"
				for p in self.procs:
					self.schedule(p)
				self.procs = []
			print "continuing on %s" %name
			self.proc_done.append(name)
			self.__proc(name)
			self.methods.append(name)
		self.write_stubs("_stubs.cpp", self.failed)
		self.methods += self.failed
		done, failed = len(self.proc_done), len(self.failed)

		self.fd.write("\n")
		self.fd.write("\n".join(self.translated))
		self.fd.write("\n")
		print "%d ok, %d failed of %d, %.02g%% translated" %(done, failed, done + failed, 100.0 * done / (done + failed))
		print "\n".join(self.failed)
		data_bin = self.data_seg
		cdata_bin = self.cdata_seg
		hdata_bin = self.hdata_seg
		data_impl = ""
		n = 0
		comment = str()

		data_impl += "\nMemory m = {\n"
		for v in cdata_bin:
			#data_impl += "0x%02x, " %v
			data_impl += "%s" %v
			n += 1

		data_impl += "};\n"
		'''
		data_impl += "\n\tuint8_t m[] = {\n\t\t"

		for v in data_bin:
			data_impl += "0x%02x, " %v
			n += 1

			comment += chr(v) if (v >= 0x20 and v < 0x7f and v != ord('\\')) else "."
			if (n & 0xf) == 0:
				data_impl += "\n\t\t//0x%04x: %s\n\t\t" %(n - 16, comment)
				comment = str()
			#elif (n & 0x3) == 0:
			#	comment += " "
		data_impl += "};\n\t//ds.assign(src, src + sizeof(src));\n"
		'''

		self.hd.write(
"""\n#include "asm.h"

//namespace %s {

"""
%(self.namespace))

		if self.skip_addr_constants == False:
			for name,addr in self.proc_addr:
				self.hd.write("static const uint16_t addr_%s = 0x%04x;\n" %(name, addr))


		#for name,addr in self.used_data_offsets:
		#	self.hd.write("static const uint16_t offset_%s = 0x%04x;\n" %(name, addr))

		offsets = []
		for k, v in self.context.get_globals().items():
			k = re.sub(r'[^A-Za-z0-9_]', '_', k)
			if isinstance(v, op.var):
				offsets.append((k.capitalize(), hex(v.offset)))
			elif isinstance(v, op.const):
				offsets.append((k.capitalize(), self.expand_equ(v.value))) #fixme: try to save all constants here

		offsets = sorted(offsets, key=lambda t: t[1])
		for o in offsets:
			self.hd.write("static const uint16_t k%s = %s;\n" %o)
		self.hd.write("\n")

		data_head = "\ntypedef struct Mem {\n"
		for v in hdata_bin:
			#data_impl += "0x%02x, " %v
			data_head += "%s" %v
			#n += 1
		data_head += "} Memory;\n"
		self.hd.write(data_head)

		self.hd.write(
"""
class %sContext {
public:
	%sContext() {}

//	void _start();
"""
%(self.namespace,self.namespace))
		if self.skip_dispatch_call == False:
			self.hd.write(
"""	
""")

		for p in set(self.methods):
			if p in self.blacklist:
				if self.header_omit_blacklisted == False:
					self.hd.write("\t//void %s();\n" %p)
			else:
				if p in self.function_name_remapping:
					self.hd.write("\tvoid %s();\n" %self.function_name_remapping[p])
				else:
					self.hd.write("\tvoid %s();\n" %p)

		self.hd.write("};\n\n//} // End of namespace DreamGen\n\n#endif\n")
		self.hd.close()

		#self.fd.write("void %sContext::__start() { %s\t%s(); \n}\n" %(self.namespace, data_impl, start))
		self.fd.write(" %s\n" %data_impl)

		if self.skip_dispatch_call == False:
			self.fd.write("\nvoid %sContext::__dispatch_call(uint16_t addr) {\n\tswitch(addr) {\n" %self.namespace)
			self.proc_addr.sort(cmp = lambda x, y: x[1] - y[1])
			for name,addr in self.proc_addr:
				self.fd.write("\t\tcase addr_%s: %s(); break;\n" %(name, name))
			self.fd.write("\t\tdefault: ::error(\"invalid call to %04x dispatched\", (uint16_t)ax);")
			self.fd.write("\n\t}\n}")

		self.fd.write("\n\n//} // End of namespace DreamGen\n")
		self.fd.close()


#x0r
	def _lea(self, dst, src):
		self.body += "\tR(%s = %s);\n" %(dst, self.extract_brackets(src))


	def _adc(self, dst, src):
		self.body += "\tR(ADC(%s, %s));\n" %self.parse2(dst, src)


	def _setnz(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(SETNZ(%s))\n" %(dst)


	def _setz(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(SETZ(%s))\n" %(dst)

	def _setb(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(SETB(%s)\n" %(dst)

	def _sbb(self, dst, src):
		self.body += "\tR(SBB(%s, %s));\n" %self.parse2(dst, src)

	def _movs(self, dst, src):
		self.body += "MOBVS(%s, %s);\n" %self.parse2(dst, src)

	def _bt(self, dst, src):
		self.body += "\tR(BT(%s, %s));\n" %self.parse2(dst, src)


	def _bts(self, dst, src):
		self.a, self.b = self.parse2(dst, src)
		self.body += "\tR(BTS(%s, %s);\n" %(self.a, self.b)

	def _ror(self, dst, src):
		self.body += "\tR(ROR(%s, %s));\n" %self.parse2(dst, src)

	def _rol(self, dst, src):
		self.body += "\tR(ROL(%s, %s));\n" %self.parse2(dst, src)


	def _sar(self, dst, src):
		self.body += "\tR(SAR(%s, %s));\n" %self.parse2(dst, src)

	def _repe(self):
		self.body += "\tREPE_"

	def _repne(self):
		self.body += "\tREPNE_"

	def _shrd(self, dst, src, c):
		self.body += "\tSHRD(%s, %s, " %self.parse2(dst, src)
		self.body += "%s);\n" %self.expand(c)

	def _loope(self, label):
		self.body += "\tR(LOOPE(%s));\n" %self.jump_to_label(label)

	def _pushf(self):
		self.body += "\tR(PUSH(flags));\n"

	def _popf(self):
		self.body += "\tR(POP(flags));\n"

	def _pushad(self):
		self.body += "\tR(PUSHAD);\n"

	def _pusha(self):
		self.body += "\tR(PUSHA);\n"

	def _popad(self):
		self.body += "\tR(POPAD);\n"

	def _popa(self):
		self.body += "\tR(POPA);\n"

	def _aad(self):
		self.body += "\tR(AAD);\n"

	def _cwde(self):
		self.body += "\tR(CWDE);\n"

	def _cwd(self):
		self.body += "\tR(CWD);\n"

	def _lods(self, src):
		src = self.expand(src)
		self.body += "\tR(LODS(%s));\n" %(src)

	def _cli(self):
		self.body += "\t// _cli();\n"

	def _sti(self):
		self.body += "\t// _sti();\n"


	def _in(self, dst, src):
		self.body += "\tR(IN(%s, %s));\n" %self.parse2(dst, src)

	def _out(self, dst, src):
		self.body += "\tR(OUT(%s, %s));\n" %self.parse2(dst, src)

	def _int(self, dst):
		dst = self.expand(dst)
		self.body += "\tR(INT(%s));\n" %(dst)
