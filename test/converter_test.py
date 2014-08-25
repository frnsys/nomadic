import shutil
from os.path import exists

from nomadic.core.builder import converter
from test import NomadicTest, note_at

from lxml.html import fromstring, tostring


html = '''
    <p>
        <span style='font-weight:bold;font-style:italic;'>
            foobar
            <span style='font-style:italic'>
                lala
                <span style='font-weight:bold;'>
                    yum
                </span>
            </span>
            hey hey
            <span style='font-weight:bold'>
                uh oh
            </span>
            yes
        </span>
    </p>
'''

class ConverterTest(NomadicTest):
    def test_html_to_markdown(self):
        markdown = converter.html_to_markdown(html)
        expected = u'_** foobar _ lala ** yum **_ hey hey ** uh oh ** yes **_\n\n'
        self.assertEqual(markdown, expected)

    def test_convert_spans(self):
        expected = '''
            <p>
                <em><strong>
                    foobar
                    <em>
                        lala
                        <strong>
                            yum
                        </strong>
                    </em>
                    <span>
                        hey hey
                    </span>
                    <strong>
                        uh oh
                    </strong>
                    <span>
                        yes
                    </span>
                </strong></em>
            </p>
        '''

        h = fromstring(html)
        for span in h.findall('.//span'):
            converter.convert_span(span)
        result = tostring(h)

        results = [x.replace('\n', '').replace(' ', '') for x in [result, expected]]
        self.assertEqual(results[0], results[1])
