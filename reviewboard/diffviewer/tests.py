from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from djblets.util.misc import cache_memoize
from kgb import SpyAgency
from reviewboard.diffviewer.chunk_generator import DiffChunkGenerator
from reviewboard.diffviewer.errors import UserVisibleError
from reviewboard.diffviewer.forms import UploadDiffForm
from reviewboard.diffviewer.models import DiffSet, FileDiff
from reviewboard.diffviewer.myersdiff import MyersDiffer
from reviewboard.diffviewer.opcode_generator import get_diff_opcode_generator
from reviewboard.diffviewer.renderers import DiffRenderer
from reviewboard.diffviewer.processors import (filter_interdiff_opcodes,
                                               merge_adjacent_chunks)
from reviewboard.diffviewer.templatetags.difftags import highlightregion
from reviewboard.scmtools.models import Repository, Tool
from reviewboard.testing import TestCase
                         [("equal", 0, 3, 0, 3), ])
                         [("delete", 0, 3, 0, 0), ])
                          ("equal", 0, 6, 2, 8)])
                         [("equal", 0, 4, 0, 4),
                          ("insert", 5, 5, 5, 9),
                          ("equal", 5, 8, 9, 12)])
        opcodes = list(MyersDiffer(a, b).get_opcodes())
        differ = MyersDiffer(a, b)
        differ.add_interesting_lines_for_headers(filename)
            self.assertTrue(file.origFile.startswith("%s/orig_src/" %
            self.assertTrue(file.newFile.startswith("%s/new_src/" %
        differ = MyersDiffer(old.splitlines(), new.splitlines())
        opcode_generator = get_diff_opcode_generator(differ)

        for opcodes in opcode_generator:
    def test_line_counts(self):
        """Testing DiffParser with insert/delete line counts"""
        diff = (
            '+ This is some line before the change\n'
            '- And another line\n'
            'Index: foo\n'
            '- One last.\n'
            '--- README  123\n'
            '+++ README  (new)\n'
            '@ -1,1 +1,1 @@\n'
            '-blah blah\n'
            '-blah\n'
            '+blah!\n'
            '-blah...\n'
            '+blah?\n'
            '-blah!\n'
            '+blah?!\n')
        files = diffparser.DiffParser(diff).parse()

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].insert_count, 3)
        self.assertEqual(files[0].delete_count, 4)
class FileDiffMigrationTests(TestCase):
    fixtures = ['test_scmtools']

    def setUp(self):
        self.diff = (
            'diff --git a/README b/README\n'
            'index d6613f5..5b50866 100644\n'
            '--- README\n'
            '+++ README\n'
            '@ -1,1 +1,1 @@\n'
            '-blah blah\n'
            '+blah!\n')
        self.parent_diff = (
            'diff --git a/README b/README\n'
            'index d6613f5..5b50866 100644\n'
            '--- README\n'
            '+++ README\n'
            '@ -1,1 +1,1 @@\n'
            '-blah..\n'
            '+blah blah\n')

        repository = self.create_repository(tool_name='Test')
        diffset = DiffSet.objects.create(name='test',
                                         revision=1,
                                         repository=repository)
        self.filediff = FileDiff(source_file='README',
                                 dest_file='README',
                                 diffset=diffset,
                                 diff64='',
                                 parent_diff64='')

    def test_migration_by_diff(self):
        """Testing FileDiffData migration accessing FileDiff.diff"""
        self.filediff.diff64 = self.diff

        self.assertEqual(self.filediff.diff_hash, None)
        self.assertEqual(self.filediff.parent_diff_hash, None)

        # This should prompt the migration
        diff = self.filediff.diff

        self.assertEqual(self.filediff.parent_diff_hash, None)
        self.assertNotEqual(self.filediff.diff_hash, None)

        self.assertEqual(diff, self.diff)
        self.assertEqual(self.filediff.diff64, '')
        self.assertEqual(self.filediff.diff_hash.binary, self.diff)
        self.assertEqual(self.filediff.diff, diff)
        self.assertEqual(self.filediff.parent_diff, None)
        self.assertEqual(self.filediff.parent_diff_hash, None)

    def test_migration_by_parent_diff(self):
        """Testing FileDiffData migration accessing FileDiff.parent_diff"""
        self.filediff.diff64 = self.diff
        self.filediff.parent_diff64 = self.parent_diff

        self.assertEqual(self.filediff.parent_diff_hash, None)

        # This should prompt the migration
        parent_diff = self.filediff.parent_diff

        self.assertNotEqual(self.filediff.parent_diff_hash, None)

        self.assertEqual(parent_diff, self.parent_diff)
        self.assertEqual(self.filediff.parent_diff64, '')
        self.assertEqual(self.filediff.parent_diff_hash.binary,
                         self.parent_diff)
        self.assertEqual(self.filediff.parent_diff, self.parent_diff)

    def test_migration_by_delete_count(self):
        """Testing FileDiffData migration accessing FileDiff.delete_count"""
        self.filediff.diff64 = self.diff

        self.assertEqual(self.filediff.diff_hash, None)

        # This should prompt the migration
        delete_count = self.filediff.delete_count

        self.assertNotEqual(self.filediff.diff_hash, None)
        self.assertEqual(delete_count, 1)
        self.assertEqual(self.filediff.diff_hash.delete_count, 1)

    def test_migration_by_insert_count(self):
        """Testing FileDiffData migration accessing FileDiff.insert_count"""
        self.filediff.diff64 = self.diff

        self.assertEqual(self.filediff.diff_hash, None)

        # This should prompt the migration
        insert_count = self.filediff.insert_count

        self.assertNotEqual(self.filediff.diff_hash, None)
        self.assertEqual(insert_count, 1)
        self.assertEqual(self.filediff.diff_hash.insert_count, 1)

    def test_migration_by_set_line_counts(self):
        """Testing FileDiffData migration calling FileDiff.set_line_counts"""
        self.filediff.diff64 = self.diff

        self.assertEqual(self.filediff.diff_hash, None)

        # This should prompt the migration, but with our line counts.
        self.filediff.set_line_counts(10, 20)

        self.assertNotEqual(self.filediff.diff_hash, None)
        self.assertEqual(self.filediff.insert_count, 10)
        self.assertEqual(self.filediff.delete_count, 20)
        self.assertEqual(self.filediff.diff_hash.insert_count, 10)
        self.assertEqual(self.filediff.diff_hash.delete_count, 20)


                          '<span class="hl">abc</span>')
                          '<span class="hl">a</span>bc')
    fixtures = ['test_scmtools']
    PREFIX = os.path.join(os.path.dirname(__file__), 'testdata')
    def test_long_filenames(self):
        repository = self.create_repository()

    def test_diff_hashes(self):
        """
        Testing that uploading two of the same diff will result in only
        one database entry.
        """
        repository = self.create_repository()
        diffset = DiffSet.objects.create(name='test',
                                         revision=1,
                                         repository=repository)
        f = open(os.path.join(self.PREFIX, "diffs", "context", "foo.c.diff"),
                 "r")
        data = f.read()
        f.close()

        filediff1 = FileDiff(diff=data,
                             diffset=diffset)
        filediff1.save()
        filediff2 = FileDiff(diff=data,
                             diffset=diffset)
        filediff2.save()

        self.assertEquals(filediff1.diff_hash, filediff2.diff_hash)


class DiffSetManagerTests(SpyAgency, TestCase):
    """Unit tests for DiffSetManager."""
    fixtures = ['test_scmtools']

    def test_creating_with_diff_data(self):
        """Test creating a DiffSet from diff file data"""
        diff = (
            'diff --git a/README b/README\n'
            'index d6613f5..5b50866 100644\n'
            '--- README\n'
            '+++ README\n'
            '@ -1,1 +1,1 @@\n'
            '-blah..\n'
            '+blah blah\n'
        )

        repository = self.create_repository(tool_name='Test')

        self.spy_on(repository.get_file_exists,
                    call_fake=lambda *args, **kwargs: True)

        diffset = DiffSet.objects.create_from_data(
            repository, 'diff', diff, None, None, None, '/', None)

        self.assertEqual(diffset.files.count(), 1)


class UploadDiffFormTests(SpyAgency, TestCase):
    """Unit tests for UploadDiffForm."""
    fixtures = ['test_scmtools']

    def test_creating_diffsets(self):
        """Test creating a DiffSet from form data"""
        diff = (
            'diff --git a/README b/README\n'
            'index d6613f5..5b50866 100644\n'
            '--- README\n'
            '+++ README\n'
            '@ -1,1 +1,1 @@\n'
            '-blah..\n'
            '+blah blah\n'
        )

        diff_file = SimpleUploadedFile('diff', diff,
                                       content_type='text/x-patch')

        repository = self.create_repository(tool_name='Test')

        self.spy_on(repository.get_file_exists,
                    call_fake=lambda *args, **kwargs: True)

        form = UploadDiffForm(
            repository=repository,
            data={
                'basedir': '/',
                'base_commit_id': '1234',
            },
            files={
                'path': diff_file,
            })
        self.assertTrue(form.is_valid())

        diffset = form.create(diff_file)
        self.assertEqual(diffset.files.count(), 1)
        self.assertEqual(diffset.basedir, '/')
        self.assertEqual(diffset.base_commit_id, '1234')

    def test_parent_diff_filtering(self):
        """Testing UploadDiffForm and filtering parent diff files"""
        saw_file_exists = {}

        def get_file_exists(repository, filename, revision, *args, **kwargs):
            saw_file_exists[(filename, revision)] = True
            return True

        diff = (
            'diff --git a/README b/README\n'
            'index d6613f5..5b50866 100644\n'
            '--- README\n'
            '+++ README\n'
            '@ -1,1 +1,1 @@\n'
            '-blah blah\n'
            '+blah!\n'
        )
        parent_diff_1 = (
            'diff --git a/README b/README\n'
            'index d6613f4..5b50865 100644\n'
            '--- README\n'
            '+++ README\n'
            '@ -1,1 +1,1 @@\n'
            '-blah..\n'
            '+blah blah\n'
        )
        parent_diff_2 = (
            'diff --git a/UNUSED b/UNUSED\n'
            'index 1234567..5b50866 100644\n'
            '--- UNUSED\n'
            '+++ UNUSED\n'
            '@ -1,1 +1,1 @@\n'
            '-foo\n'
            '+bar\n'
        )
        parent_diff = parent_diff_1 + parent_diff_2

        diff_file = SimpleUploadedFile('diff', diff,
                                       content_type='text/x-patch')
        parent_diff_file = SimpleUploadedFile('parent_diff', parent_diff,
                                              content_type='text/x-patch')

        repository = self.create_repository(tool_name='Test')
        self.spy_on(repository.get_file_exists, call_fake=get_file_exists)

        form = UploadDiffForm(
            repository=repository,
            data={
                'basedir': '/',
            },
            files={
                'path': diff_file,
                'parent_diff_path': parent_diff_file,
            })
        self.assertTrue(form.is_valid())

        diffset = form.create(diff_file, parent_diff_file)
        self.assertEqual(diffset.files.count(), 1)

        filediff = diffset.files.get()
        self.assertEqual(filediff.diff, diff)
        self.assertEqual(filediff.parent_diff, parent_diff_1)

        self.assertTrue(('/README', 'd6613f4') in saw_file_exists)
        self.assertFalse(('/UNUSED', '1234567') in saw_file_exists)
        self.assertEqual(len(saw_file_exists), 1)

    def test_mercurial_parent_diff_base_rev(self):
        """Testing that the correct base revision is used for Mercurial diffs"""
        diff = (
            '# Node ID a6fc203fee9091ff9739c9c00cd4a6694e023f48\n'
            '# Parent  7c4735ef51a7c665b5654f1a111ae430ce84ebbd\n'
            'diff --git a/doc/readme b/doc/readme\n'
            '--- a/doc/readme\n'
            '+++ b/doc/readme\n'
            '@@ -1,3 +1,3 @@\n'
            ' Hello\n'
            '-\n'
            '+...\n'
            ' goodbye\n'
        )

        parent_diff = (
            '# Node ID 7c4735ef51a7c665b5654f1a111ae430ce84ebbd\n'
            '# Parent  661e5dd3c4938ecbe8f77e2fdfa905d70485f94c\n'
            'diff --git a/doc/newfile b/doc/newfile\n'
            'new file mode 100644\n'
            '--- /dev/null\n'
            '+++ b/doc/newfile\n'
            '@@ -0,0 +1,1 @@\n'
            '+Lorem ipsum\n'
        )

        diff_file = SimpleUploadedFile('diff', diff,
                                       content_type='text/x-patch')
        parent_diff_file = SimpleUploadedFile('parent_diff', parent_diff,
                                              content_type='text/x-patch')

        repository = Repository.objects.create(
            name='Test HG',
            path='scmtools/testdata/hg_repo.bundle',
            tool=Tool.objects.get(name='Mercurial'))

        form = UploadDiffForm(
            repository=repository,
            files={
                'path': diff_file,
                'parent_diff_path': parent_diff_file,
            })
        self.assertTrue(form.is_valid())

        diffset = form.create(diff_file, parent_diff_file)
        self.assertEqual(diffset.files.count(), 1)

        filediff = diffset.files.get()

        self.assertEqual(filediff.source_revision,
                         '661e5dd3c4938ecbe8f77e2fdfa905d70485f94c')


class ProcessorsTests(TestCase):
    """Unit tests for diff processors."""

    def test_filter_interdiff_opcodes(self):
        """Testing filter_interdiff_opcodes"""
        opcodes = [
            ('insert', 0, 0, 0, 1),
            ('equal', 0, 5, 1, 5),
            ('delete', 5, 10, 5, 5),
            ('equal', 10, 25, 5, 20),
            ('replace', 25, 26, 20, 26),
            ('equal', 26, 40, 26, 40),
            ('insert', 40, 40, 40, 45),
        ]

        # NOTE: Only the "@@" lines in the diff matter below for this
        #       processor, so the rest can be left out.
        orig_diff = '@@ -22,7 +22,7 @@\n'
        new_diff = (
            '@@ -2,11 +2,6 @@\n'
            '@@ -22,7 +22,7 @@\n'
        )

        new_opcodes = list(filter_interdiff_opcodes(opcodes, orig_diff,
                                                    new_diff))

        self.assertEqual(new_opcodes, [
            ('equal', 0, 0, 0, 1),
            ('equal', 0, 5, 1, 5),
            ('delete', 5, 10, 5, 5),
            ('equal', 10, 25, 5, 20),
            ('replace', 25, 26, 20, 26),
            ('equal', 26, 40, 26, 40),
            ('equal', 40, 40, 40, 45),
        ])

    def test_filter_interdiff_opcodes_with_inserts_right(self):
        """Testing filter_interdiff_opcodes with inserts on the right"""
        # These opcodes were taken from the r1-r2 interdiff at
        # http://reviews.reviewboard.org/r/4221/
        opcodes = [
            ('equal', 0, 141, 0, 141),
            ('replace', 141, 142, 141, 142),
            ('insert', 142, 142, 142, 144),
            ('equal', 142, 165, 144, 167),
            ('replace', 165, 166, 167, 168),
            ('insert', 166, 166, 168, 170),
            ('equal', 166, 190, 170, 194),
            ('insert', 190, 190, 194, 197),
            ('equal', 190, 232, 197, 239),
        ]

        # NOTE: Only the "@@" lines in the diff matter below for this
        #       processor, so the rest can be left out.
        orig_diff = '@@ -0,0 +1,232 @@\n'
        new_diff = '@@ -0,0 +1,239 @@\n'

        new_opcodes = list(filter_interdiff_opcodes(opcodes, orig_diff,
                                                    new_diff))

        self.assertEqual(new_opcodes, [
            ('equal', 0, 141, 0, 141),
            ('replace', 141, 142, 141, 142),
            ('insert', 142, 142, 142, 144),
            ('equal', 142, 165, 144, 167),
            ('replace', 165, 166, 167, 168),
            ('insert', 166, 166, 168, 170),
            ('equal', 166, 190, 170, 194),
            ('insert', 190, 190, 194, 197),
            ('equal', 190, 232, 197, 239),
        ])

    def test_merge_adjacent_chunks(self):
        """Testing merge_adjacent_chunks"""
        opcodes = [
            ('equal', 0, 0, 0, 1),
            ('equal', 0, 5, 1, 5),
            ('delete', 5, 10, 5, 5),
            ('equal', 10, 25, 5, 20),
            ('replace', 25, 26, 20, 26),
            ('equal', 26, 40, 26, 40),
            ('equal', 40, 40, 40, 45),
        ]

        new_opcodes = list(merge_adjacent_chunks(opcodes))

        self.assertEqual(new_opcodes, [
            ('equal', 0, 5, 0, 5),
            ('delete', 5, 10, 5, 5),
            ('equal', 10, 25, 5, 20),
            ('replace', 25, 26, 20, 26),
            ('equal', 26, 40, 26, 45),
        ])


class DiffChunkGeneratorTests(TestCase):
    """Unit tests for DiffChunkGenerator."""
    def test_get_line_changed_regions(self):
        """Testing DiffChunkGenerator._get_line_changed_regions"""
        def deep_equal(A, B):
            typea, typeb = type(A), type(B)
            self.assertEqual(typea, typeb)
            if typea is tuple or typea is list:
                for a, b in map(None, A, B):
                    deep_equal(a, b)
            else:
                self.assertEqual(A, B)

        filediff = FileDiff(source_file='foo', diffset=DiffSet())
        generator = DiffChunkGenerator(None, filediff)

        deep_equal(generator._get_line_changed_regions(None, None),
                   (None, None))

        old = 'submitter = models.ForeignKey(Person, verbose_name="Submitter")'
        new = 'submitter = models.ForeignKey(User, verbose_name="Submitter")'
        regions = generator._get_line_changed_regions(old, new)
        deep_equal(regions, ([(30, 36)], [(30, 34)]))

        old = '-from reviews.models import ReviewRequest, Person, Group'
        new = '+from .reviews.models import ReviewRequest, Group'
        regions = generator._get_line_changed_regions(old, new)
        deep_equal(regions, ([(0, 1), (6, 6), (43, 51)],
                             [(0, 1), (6, 7), (44, 44)]))

        old = 'abcdefghijklm'
        new = 'nopqrstuvwxyz'
        regions = generator._get_line_changed_regions(old, new)
        deep_equal(regions, (None, None))


class DiffRendererTests(SpyAgency, TestCase):
    """Unit tests for DiffRenderer."""
    def test_construction_with_invalid_chunks(self):
        """Testing DiffRenderer construction with invalid chunks"""
        diff_file = {
            'chunks': [{}]
        }

        self.assertRaises(
            UserVisibleError,
            lambda: DiffRenderer(diff_file, chunk_index=-1))
        self.assertRaises(
            UserVisibleError,
            lambda: DiffRenderer(diff_file, chunk_index=1))

    def test_construction_with_valid_chunks(self):
        """Testing DiffRenderer construction with valid chunks"""
        diff_file = {
            'chunks': [{}]
        }

        # Should not assert.
        renderer = DiffRenderer(diff_file, chunk_index=0)
        self.assertEqual(renderer.num_chunks, 1)
        self.assertEqual(renderer.chunk_index, 0)

    def test_render_to_response(self):
        """Testing DiffRenderer.render_to_response"""
        diff_file = {
            'chunks': [{}]
        }

        renderer = DiffRenderer(diff_file)
        self.spy_on(renderer.render_to_string, call_fake=lambda self: 'Foo')

        response = renderer.render_to_response()

        self.assertTrue(renderer.render_to_string.called)
        self.assertTrue(isinstance(response, HttpResponse))
        self.assertEqual(response.content, 'Foo')

    def test_render_to_string(self):
        """Testing DiffRenderer.render_to_string"""
        diff_file = {
            'chunks': [{}]
        }

        renderer = DiffRenderer(diff_file)
        self.spy_on(renderer.render_to_string_uncached,
                    call_fake=lambda self: 'Foo')
        self.spy_on(renderer.make_cache_key,
                    call_fake=lambda self: 'my-cache-key')
        self.spy_on(cache_memoize)

        response = renderer.render_to_response()

        self.assertEqual(response.content, 'Foo')
        self.assertTrue(renderer.render_to_string_uncached.called)
        self.assertTrue(renderer.make_cache_key.called)
        self.assertTrue(cache_memoize.spy.called)

    def test_render_to_string_uncached(self):
        """Testing DiffRenderer.render_to_string_uncached"""
        diff_file = {
            'chunks': [{}]
        }

        renderer = DiffRenderer(diff_file, lines_of_context=[5, 5])
        self.spy_on(renderer.render_to_string_uncached,
                    call_fake=lambda self: 'Foo')
        self.spy_on(renderer.make_cache_key,
                    call_fake=lambda self: 'my-cache-key')
        self.spy_on(cache_memoize)

        response = renderer.render_to_response()

        self.assertEqual(response.content, 'Foo')
        self.assertTrue(renderer.render_to_string_uncached.called)
        self.assertFalse(renderer.make_cache_key.called)
        self.assertFalse(cache_memoize.spy.called)

    def test_make_context_with_chunk_index(self):
        """Testing DiffRenderer.make_context with chunk_index"""
        diff_file = {
            'newfile': True,
            'interfilediff': None,
            'filediff': FileDiff(),
            'chunks': [
                {
                    'lines': [],
                    'meta': {},
                    'change': 'insert',
                },
                {
                    # This is not how lines really look, but it's fine for
                    # current usage tests.
                    'lines': range(10),
                    'meta': {},
                    'change': 'replace',
                },
                {
                    'lines': [],
                    'meta': {},
                    'change': 'delete',
                }
            ],
        }

        renderer = DiffRenderer(diff_file, chunk_index=1)
        context = renderer.make_context()

        self.assertEqual(context['standalone'], True)
        self.assertEqual(context['file'], diff_file)
        self.assertEqual(len(diff_file['chunks']), 1)

        chunk = diff_file['chunks'][0]
        self.assertEqual(chunk['change'], 'replace')