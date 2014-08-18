from nomadic import extractor
from test import NomadicTest, note_at

class ExtractorTest(NomadicTest):
    def test_extract_html_note_removes_html(self):
        note = extractor.note_from_path(note_at('test.html'))
        data = extractor.process_note(note)

        self.assertEqual(data['title'], 'test')
        self.assertEqual(data['path'], note_at('test.html'))
        self.assertEqual(data['content'], 'Test HTML\n\n\n\n\n    This is a test')

    def test_extract_pdf_note(self):
        note = extractor.note_from_path(note_at('womp.pdf'))
        data = extractor.process_note(note)

        self.assertEqual(data['title'], 'womp')
        self.assertEqual(data['path'], note_at('womp.pdf'))
        self.assertEqual(data['content'], 'I\'m a PDF')

    def test_extract_markdown_note(self):
        note = extractor.note_from_path(note_at('my note.md'))
        data = extractor.process_note(note)

        self.assertEqual(data['title'], 'my note')
        self.assertEqual(data['path'], note_at('my note.md'))
        self.assertEqual(data['content'], 'HEY HI\nfoo bar qua')


