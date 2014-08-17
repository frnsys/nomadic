from nomad import searcher, indexer
from test import NomadTest, note_at

class SearcherTest(NomadTest):
    def test_search(self):
        self.index = indexer.Index(self.notes_dir)
        self.index.reset()

        results = [result for result in searcher.search('hullo', self.index)]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].data['path'], note_at('some_notebook/a cool note.md'))
