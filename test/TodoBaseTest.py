# Topydo - A todo.txt client written in Python.
# Copyright (C) 2014 Bram Schoenmakers <me@bramschoenmakers.nl>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Tests for the TodoBase class. """

from datetime import date
import re
import unittest

import TodoBase

class TodoBaseTester(unittest.TestCase):
    def test_parse_tag(self):
        todo = TodoBase.TodoBase("(C) Test foo:bar foo:baz foo_:baz_ blah:zah:haz")

        self.assertTrue(todo.has_tag('foo'))
        self.assertTrue(todo.has_tag('foo_'))
        self.assertTrue(todo.has_tag('foo', 'bar'))
        self.assertTrue(todo.has_tag('foo', 'baz'))
        self.assertTrue(todo.has_tag('blah'))
        self.assertTrue(todo.has_tag('blah', 'zah:haz'))

    def test_add_tag1(self):
        todo = TodoBase.TodoBase("(C) Foo")
        todo.set_tag('foo', 'bar')

        self.assertTrue(todo.has_tag('foo'))
        self.assertTrue(todo.has_tag('foo', 'bar'))
        self.assertFalse(todo.has_tag('foo', 'baz'))
        self.assertFalse(todo.has_tag('bar'))
        self.assertTrue(re.search(r'\bfoo:bar\b', todo.src))

    def test_add_tag2(self):
        todo = TodoBase.TodoBase("(C) Foo id:1")
        todo.add_tag('id', '2')

        self.assertEquals(todo.source(), '(C) Foo id:1 id:2')

    def test_set_tag(self):
        todo = TodoBase.TodoBase("(C) Foo foo:bar")
        todo.set_tag('foo', 'baz')

        self.assertTrue(todo.has_tag('foo'))
        self.assertTrue(todo.has_tag('foo', 'baz'))
        self.assertFalse(todo.has_tag('foo', 'bar'))

        self.assertTrue(re.search(r'\bfoo:baz\b', todo.src))
        self.assertFalse(re.search(r'\bfoo:bar\b', todo.src))

    def test_set_tag_double_value(self):
        todo = TodoBase.TodoBase("(C) Foo foo:bar baz:bar")
        todo.set_tag('foo', 'blah');

        self.assertTrue(todo.has_tag('foo'))
        self.assertTrue(todo.tag_value('foo'), 'blah')
        self.assertTrue(todo.has_tag('baz'))
        self.assertTrue(todo.tag_value('baz'), 'bar')

    def test_set_tag_double_tag(self):
        todo = TodoBase.TodoBase("(C) Foo foo:bar foo:baz")
        todo.set_tag('foo', 'blah')

        self.assertTrue(todo.has_tag('foo', 'blah'))
        self.assertTrue(todo.has_tag('foo', 'bar') or todo.has_tag('foo', 'baz'))

    def test_set_tag_empty_value(self):
        todo = TodoBase.TodoBase("(C) Foo foo:bar foo:baz")
        todo.set_tag('foo')

        self.assertFalse(todo.has_tag('foo'))
        self.assertFalse(re.search(r'\bfoo:', todo.src))

    def test_remove_all(self):
        todo = TodoBase.TodoBase("(C) Foo foo:bar foo:baz foo:")
        todo.remove_tag('foo')

        self.assertFalse(todo.has_tag('foo'))
        self.assertFalse(re.search(r'\bfoo:(bar|baz)\b', todo.src))
        self.assertTrue(re.search(r'foo:', todo.src))

    def test_remove_specific_tag_value(self):
        todo = TodoBase.TodoBase("(C) Foo kungfoo:bar foo:bar foo:barz")
        todo.remove_tag('foo', 'bar')

        self.assertTrue(todo.has_tag('foo'))
        self.assertTrue(todo.has_tag('kungfoo', 'bar'))
        self.assertTrue(todo.has_tag('foo', 'barz'))
        self.assertFalse(todo.has_tag('foo', 'bar'))

        self.assertTrue(re.search(r'\bkungfoo:bar\b', todo.src))
        self.assertTrue(re.search(r'\bfoo:barz\b', todo.src))
        self.assertFalse(re.search(r'\bfoo:bar\b', todo.src))

    def test_set_priority1(self):
        """ Change priority. """
        todo = TodoBase.TodoBase("(A) Foo")
        todo.set_priority('B')

        self.assertEquals(todo.priority(), 'B')
        self.assertTrue(re.match(r'^\(B\) Foo$', todo.src))

    def test_set_priority2(self):
        """ Set priority to task without priority. """
        todo = TodoBase.TodoBase("Foo")
        todo.set_priority('B')

        self.assertEquals(todo.priority(), 'B')
        self.assertTrue(re.match(r'^\(B\) Foo$', todo.src))

    def test_set_priority3(self):
        """ Test invalid priority input. """
        todo = TodoBase.TodoBase("(A) Foo")
        todo.set_priority('AB')

        self.assertEquals(todo.priority(), 'A')
        self.assertTrue(re.match(r'^\(A\) Foo$', todo.src))

    def test_set_priority4(self):
        """ Add priority, while not be mistaken about todo string. """
        todo = TodoBase.TodoBase("(A)Foo")

        self.assertNotEqual(todo.priority(), 'A')

        todo.set_priority('B')

        self.assertEquals(todo.priority(), 'B')
        self.assertTrue(re.match(r'^\(B\) \(A\)Foo$', todo.src))

    def test_set_priority5(self):
        """ Unset priority. """
        todo = TodoBase.TodoBase("(A) Foo")
        todo.set_priority(None)

        self.assertEquals(todo.priority(), None)
        self.assertTrue(re.match(r'^Foo$', todo.src))

    def test_set_priority6(self):
        """ Do not set priorities on completed tasks. """
        todo = TodoBase.TodoBase("x 2014-06-13 Foo")
        todo.set_priority('A')

        self.assertFalse(todo.priority())
        self.assertEquals(todo.src, "x 2014-06-13 Foo")

    def test_project1(self):
        todo = TodoBase.TodoBase("(C) Foo +Bar +Baz +Bar:")

        self.assertEquals(len(todo.projects()), 2)
        self.assertIn('Bar', todo.projects())
        self.assertIn('Baz', todo.projects())

    def test_project2(self):
        todo = TodoBase.TodoBase("(C) Foo +Bar+Baz")

        self.assertEquals(len(todo.projects()), 1)
        self.assertIn('Bar+Baz', todo.projects())

    def test_context1(self):
        todo = TodoBase.TodoBase("(C) Foo @Bar @Baz @Bar:")

        self.assertEquals(len(todo.contexts()), 2)
        self.assertIn('Bar', todo.contexts())
        self.assertIn('Baz', todo.contexts())

    def test_context2(self):
        todo = TodoBase.TodoBase("(C) Foo @Bar+Baz")

        self.assertEquals(len(todo.contexts()), 1)
        self.assertIn('Bar+Baz', todo.contexts())

    def test_completion1(self):
        todo = TodoBase.TodoBase("x 2014-06-09 Foo")

        self.assertTrue(todo.is_completed())

    def test_completion2(self):
        todo = TodoBase.TodoBase("xx Important xx")

        self.assertFalse(todo.is_completed())

    def test_completion3(self):
        """ A completed todo must start with an x followed by a date. """
        todo = TodoBase.TodoBase("x Not complete")

        self.assertFalse(todo.is_completed())

    def test_completion4(self):
        """ A completed todo must start with an x followed by a date. """
        todo = TodoBase.TodoBase("X 2014-06-14 Not complete")

        self.assertFalse(todo.is_completed())

    def test_set_complete1(self):
        todo = TodoBase.TodoBase("(A) Foo")
        todo.set_completed()

        today = date.today()
        today_str = today.isoformat()

        self.assertFalse(todo.priority())
        self.assertEquals(todo.fields['completionDate'], today)
        self.assertTrue(re.match('^x ' + today_str + ' Foo', todo.src))

    def test_set_complete2(self):
        todo = TodoBase.TodoBase("2014-06-12 Foo")
        todo.set_completed()

        today = date.today()
        today_str = today.isoformat()

        self.assertEquals(todo.fields['completionDate'], today)
        self.assertTrue(re.match('^x ' + today_str + ' 2014-06-12 Foo', \
            todo.src))

    def test_set_complete3(self):
        todo = TodoBase.TodoBase("Foo")
        todo.set_completed()

        today = date.today()
        today_str = today.isoformat()

        self.assertEquals(todo.fields['completionDate'], today)
        self.assertTrue(re.match('^x ' + today_str + ' Foo', todo.src))

    def test_set_complete4(self):
        todo = TodoBase.TodoBase("(A) 2014-06-12 Foo")
        todo.set_completed()

        today = date.today()
        today_str = today.isoformat()

        self.assertEquals(todo.fields['completionDate'], today)
        self.assertTrue(re.match('^x ' + today_str + ' 2014-06-12 Foo', todo.src))

    def test_set_complete5(self):
        todo = TodoBase.TodoBase("x 2014-06-13 Foo")
        todo.set_completed()

        self.assertEquals(todo.src, "x 2014-06-13 Foo")

    def test_set_source_text(self):
        todo = TodoBase.TodoBase("(B) Foo")

        new_text = "(C) Foo"
        todo.set_source_text(new_text)

        self.assertEquals(todo.src, new_text)
        self.assertEquals(todo.priority(),'C')

    def test_set_creation_date1(self):
        todo = TodoBase.TodoBase("Foo")
        creation_date = date(2014, 7, 24)

        todo.set_creation_date(creation_date)

        self.assertEquals(todo.creation_date(), creation_date)
        self.assertEquals(todo.src, "2014-07-24 Foo")

    def test_set_creation_date2(self):
        todo = TodoBase.TodoBase("(A) Foo")
        creation_date = date(2014, 7, 24)

        todo.set_creation_date(creation_date)

        self.assertEquals(todo.creation_date(), creation_date)
        self.assertEquals(todo.src, "(A) 2014-07-24 Foo")

    def test_set_creation_date3(self):
        todo = TodoBase.TodoBase("(A) 2014-07-23 Foo")
        creation_date = date(2014, 7, 24)

        todo.set_creation_date(creation_date)

        self.assertEquals(todo.creation_date(), creation_date)
        self.assertEquals(todo.src, "(A) 2014-07-24 Foo")

    def test_set_creation_date4(self):
        todo = TodoBase.TodoBase("2014-07-23 Foo")
        creation_date = date(2014, 7, 24)

        todo.set_creation_date(creation_date)

        self.assertEquals(todo.creation_date(), creation_date)
        self.assertEquals(todo.src, "2014-07-24 Foo")

    def test_set_creation_date5(self):
        todo = TodoBase.TodoBase("x 2014-07-25 2014-07-23 Foo")
        creation_date = date(2014, 7, 24)

        todo.set_creation_date(creation_date)

        self.assertEquals(todo.creation_date(), creation_date)
        self.assertEquals(todo.src, "x 2014-07-25 2014-07-24 Foo")

if __name__ == '__main__':
    unittest.main()
