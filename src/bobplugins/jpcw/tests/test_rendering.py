# -*- coding: utf-8 -*-

from shutil import rmtree
from tempfile import mkdtemp
import codecs
import os
import stat
import unittest

import mock
import six


class render_structureTest(unittest.TestCase):

    def setUp(self):
        import bobplugins.jpcw
        self.fs_tempdir = mkdtemp()
        self.fs_templates = os.path.abspath(
            os.path.join(os.path.dirname(bobplugins.jpcw.__file__),
                         'tests', 'templates'))

    def tearDown(self):
        rmtree(self.fs_tempdir)

    def call_FUT(self, template, variables, output_dir=None, verbose=True,
            renderer=None, ignored_files=[]):
        from mrbob.rendering import render_structure
        from mrbob.rendering import jinja2_renderer

        if output_dir is None:
            output_dir = self.fs_tempdir

        if renderer is None:
            renderer = jinja2_renderer

        render_structure(
            template,
            output_dir,
            variables,
            verbose,
            renderer,
            ignored_files,
        )

    def test_subdirectories_created(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'unbound'),
            {'ip_addr': '192.168.0.1', 'access_control': '10.0.1.0/16 allow',
              'rdr.me': 'y'},
            renderer=python_formatting_renderer,
        )
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'usr/local/etc')))

    def test_subdirectories_not_created(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'unbound'),
            {'ip_addr': '192.168.0.1', 'access_control': '10.0.1.0/16 allow',
              'rdr.me': 'f'},
            renderer=python_formatting_renderer,
        )
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir, 'usr/local/etc')))
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'etc')))
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'etc/rc.conf')))

    def test_skip_mrbobini_copying(self):
        self.call_FUT(
            os.path.join(self.fs_templates, 'skip_mrbobini'),
            dict(foo='123'),
        )
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'test')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir, '.mrbob.ini')))

    def test_ds_store(self):
        self.call_FUT(
            os.path.join(self.fs_templates, 'ds_store'),
            dict(),
        )
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir, '.mrbob.ini')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir, '.DS_Store')))

    def test_ignored(self):
        self.call_FUT(
            os.path.join(self.fs_templates, 'ignored'),
            dict(),
            ignored_files=['ignored', '*.txt', '.mrbob.ini'],
        )
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir, '.mrbob.ini')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir, 'ignored')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
            'ignored.txt')))
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'not_ignored')))

#    def test_encoding_is_utf8(self):
#        from mrbob.rendering import python_formatting_renderer
#        if six.PY3:  # pragma: no cover
#            folder_name = 'encodingč'
#        else:  # pragma: no cover
#            folder_name = 'encodingč'.decode('utf-8')
#
#        self.call_FUT(
#            os.path.join(self.fs_templates, folder_name),
#            dict(),
#            renderer=python_formatting_renderer,
#        )
#
#        if six.PY3:  # pragma: no cover
#            file_name = 'mapča/ća'
#            expected = 'Ćača.\n'
#        else:  # pragma: no cover
#            file_name = 'mapča/ća'.decode('utf-8')
#            expected = 'Ćača.\n'.decode('utf-8')
#
#        with codecs.open(os.path.join(self.fs_tempdir, file_name), 'r', 'utf-8') as f:
#            self.assertEquals(f.read(), expected)

    def test_string_replacement(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'unbound'),
            {'ip_addr': '192.168.0.1', 'access_control': '10.0.1.0/16 allow',
              'rdr.me': 'y'},
            verbose=False,
            renderer=python_formatting_renderer,
        )
        fs_unbound_conf = os.path.join(self.fs_tempdir, 'usr/local/etc/unbound/unbound.conf')
        self.assertTrue('interface: 192.168.0.1' in open(fs_unbound_conf).read())

    def test_directory_is_renamed(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'renamedir'),
            {'name': 'blubber', 'rdr.me': 'y'},
            verbose=False,
            renderer=python_formatting_renderer,
        )
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, '/partsblubber/part')))

    def test_copied_file_is_renamed(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'renamedfile'),
            {'name': 'blubber', 'rdr.me': 'y'},
            verbose=False,
            renderer=python_formatting_renderer,
        )
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, '/foo.blubber.rst')))

    def test_rendered_file_is_renamed(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'renamedtemplate'),
            {'name': 'blubber', 'rdr.me': 'y', 'module': 'blather'},
            verbose=False,
            renderer=python_formatting_renderer,
        )
        fs_rendered = '%s/%s' % (self.fs_tempdir, '/blubber_endpoint.py')
        self.assertTrue(os.path.exists(fs_rendered))
        self.assertTrue('from blather import bar' in open(fs_rendered).read())

    def test_rendered_file_is_renamed_dotted_name(self):
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'renamedtemplate2'),
            {'author.name': 'foo', 'rdr.me': 'y'},
            verbose=False,
            renderer=python_formatting_renderer,
        )
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  '/foo_endpoint.py')))

    def test_compount_renaming(self):
        """ all of the above edgecases in one fixture """
        from mrbob.rendering import python_formatting_renderer
        self.call_FUT(
            os.path.join(self.fs_templates, 'renamed'),
            {'name': 'blubber', 'rdr.me': 'y', 'module': 'blather'},
            verbose=False,
            renderer=python_formatting_renderer,
        )
        fs_rendered = '%s/%s' % (self.fs_tempdir, '/blatherparts/blubber_etc/blubber.conf')
        self.assertTrue(os.path.exists(fs_rendered))
        self.assertTrue('blather = blubber' in open(fs_rendered).read())


class render_templateTest(unittest.TestCase):
    def setUp(self):
        import bobplugins.jpcw
        self.fs_tempdir = mkdtemp()
        self.fs_templates = os.path.abspath(
            os.path.join(os.path.dirname(bobplugins.jpcw.__file__),
                         'tests', 'templates'))

    def tearDown(self):
        rmtree(self.fs_tempdir)

    def call_FUT(self, template, variables, output_dir=None, verbose=False, renderer=None):
        from mrbob.rendering import render_template
        from mrbob.rendering import python_formatting_renderer

        if output_dir is None:
            output_dir = self.fs_tempdir

        if renderer is None:
            renderer = python_formatting_renderer

        return render_template(
            template,
            output_dir,
            variables,
            verbose,
            renderer,
        )

    def test_render_copy(self):
        """if the source is not a template, it is copied."""
        fs_source = os.path.join(self.fs_templates, 'unbound/etc/rc.conf')

        fs_rendered = self.call_FUT(
            fs_source,
            {'ip_addr': '192.168.0.1', 'access_control': '10.0.1.0/16 allow',
              'rdr.me': 'y'},)
        self.assertTrue(fs_rendered.endswith('rc.conf'))
        with open(fs_source) as f1:
            with open(fs_rendered) as f2:
                self.assertEqual(f1.read(), f2.read())

    def test_render_statement_template(self):
        """if the source is not a template, it is copied."""
        filename = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bob'
        fs_source = os.path.join(self.fs_templates, filename)
        self.call_FUT(fs_source, {'rdr.me': 'y', 'author.name': 'bob'},)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'bob_endpoint.py')))

    def test_render_false_statement_template_is_None(self):
        """if the source is not a template, it is copied."""
        filename = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bob'
        fs_source = os.path.join(self.fs_templates, filename)
        fs_rendered = self.call_FUT(
            fs_source,
            {'rdr.me': 'n'},)
        self.assertEquals(fs_rendered, None)

    def test_render_any_non_true_value_statement_template_is_None(self):
        """if the source is not a template, it is copied."""
        filename = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bob'
        fs_source = os.path.join(self.fs_templates, filename)
        fs_rendered = self.call_FUT(
            fs_source,
            {'rdr.me': 'any value here'},)

        self.assertEquals(fs_rendered, None)

    def test_render_key_error_statement_template(self):
        """if the source is not a template, it is copied."""
        filename = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bob'
        t = os.path.join(self.fs_templates, filename)
        self.assertRaises(KeyError,
                          self.call_FUT,
                          t,
                          {'another_rdr.me': 'y'}
                          )

    def test_render_template(self):
        """if the source is a template, it is rendered and the target file drops
        the `.bob` suffix."""
        fs_source = os.path.join(self.fs_templates,
            'unbound/+__if_rdr.me__+usr/local/etc/unbound/unbound.conf.bob')
        fs_rendered = self.call_FUT(
            fs_source,
            {'ip_addr': '192.168.0.1', 'access_control': '10.0.1.0/16 allow',
              'rdr.me': 'y'})
        self.assertTrue(fs_rendered.endswith('/unbound.conf'))
        self.assertTrue('interface: 192.168.0.1' in open(fs_rendered).read())

    def test_rendered_permissions_preserved(self):
        fs_source = os.path.join(self.fs_templates,
            'unbound/+__if_rdr.me__+usr/local/etc/unbound/unbound.conf.bob')
        os.chmod(fs_source, 771)
        fs_rendered = self.call_FUT(
            fs_source,
            {'ip_addr': '192.168.0.1', 'access_control': '10.0.1.0/16 allow',
              'rdr.me': 'y'})
        self.assertEqual(stat.S_IMODE(os.stat(fs_rendered).st_mode), 771)

    def test_render_missing_key(self):
        t = os.path.join(self.fs_templates,
            'unbound/+__if_rdr.me__+usr/local/etc/unbound/unbound.conf.bob')

        self.assertRaises(KeyError,
                          self.call_FUT,
                          t,
                          dict())

    def test_render_namespace(self):
        t = os.path.join(self.fs_templates,
            'missing_namespace_key/foo.bob')

        filename = self.call_FUT(t, {'foo.bar': '1'})
        with open(filename) as f:
            self.assertEqual(f.read(), '1\n')

    def test_render_namespace_jinja2(self):
        from mrbob.rendering import jinja2_renderer
        t = os.path.join(self.fs_templates,
            'missing_namespace_key/foo_jinja2.bob')

        filename = self.call_FUT(t,
                                 {'foo.bar': '2'},
                                 renderer=jinja2_renderer)
        with open(filename) as f:
            self.assertEqual(f.read(), '2\n')

    def test_render_newline(self):
        from mrbob.rendering import jinja2_renderer
        t = os.path.join(self.fs_templates,
            'missing_namespace_key/foo_jinja2.bob')

        tfile = open(t, 'r')
        self.assertEqual(tfile.read(), '{{{foo.bar}}}\n')

        filename = self.call_FUT(t,
                                 {'foo.bar': '2'},
                                 renderer=jinja2_renderer)
        with open(filename) as f:
            self.assertEqual(f.read(), '2\n')

    def test_render_namespace_missing_key(self):
        t = os.path.join(self.fs_templates,
            'missing_namespace_key/foo.bob')

        self.assertRaises(KeyError,
                          self.call_FUT,
                          t,
                          {})

    def test_render_missing_key_statement(self):
        t = os.path.join(self.fs_templates,
            'missing_namespace_key/foo.bob')

        self.assertRaises(KeyError,
                          self.call_FUT,
                          t,
                          {'rdr.me': 'y'})

    def test_render_namespace_missing_key_jinja2(self):
        from jinja2 import UndefinedError
        from mrbob.rendering import jinja2_renderer
        t = os.path.join(self.fs_templates,
            'missing_namespace_key/foo_jinja2.bob')

        self.assertRaises(UndefinedError,
                          self.call_FUT,
                          t,
                          {},
                          renderer=jinja2_renderer)

    def test_jinja2_strict_undefined(self):
        from jinja2 import UndefinedError
        from mrbob.rendering import jinja2_renderer

        t = os.path.join(self.fs_templates,
            'strict_undefined.bob')

        self.assertRaises(UndefinedError,
                          self.call_FUT,
                          t,
                          {},
                          renderer=jinja2_renderer)


class render_filenameTest(unittest.TestCase):

    def call_FUT(self, filename, variables):
        from mrbob.rendering import render_filename
        return render_filename(filename, variables)

    def test_filename_substitution(self):
        t = self.call_FUT('em0_+ip_addr+.conf', dict(ip_addr='127.0.0.1'))
        self.assertEqual(t, 'em0_127.0.0.1.conf')

    def test_filename_nested(self):
        t = self.call_FUT('em0_+ip.addr+.conf', {'ip.addr': '127.0.0.1'})
        self.assertEqual(t, 'em0_127.0.0.1.conf')

    def test_multiple_filename_substitution(self):
        t = self.call_FUT('+device+_+ip_addr+.conf',
                          dict(ip_addr='127.0.0.1', device='em0'))
        self.assertEqual(t, 'em0_127.0.0.1.conf')

    def test_single_plus_not_substituted(self):
        t = self.call_FUT('foo+bar',
                          dict(foo='127.0.0.1', bar='em0'))
        self.assertEqual(t, 'foo+bar')

    def test_no_substitution(self):
        t = self.call_FUT('foobar',
                          dict(foo='127.0.0.1', bar='em0'))
        self.assertEqual(t, 'foobar')

    def test_pluses_in_path(self):
        t = self.call_FUT('+/bla/+/+bar+',
                          dict(bar='em0'))
        self.assertEqual(t, '+/bla/+/em0')

    @mock.patch('mrbob.rendering.os', sep='\\')
    def test_pluses_in_pathwindows(self, mock_sep):
        t = self.call_FUT('+\\bla\\+\\+bar+',
                          dict(bar='em0'))
        self.assertEqual(t, '+\\bla\\+\\em0')

    def test_missing_key(self):
        self.assertRaises(KeyError, self.call_FUT, 'foo+bar+blub', dict())

# vim:set et sts=4 ts=4 tw=80:
