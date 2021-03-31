import pytest
from textwrap import dedent, indent

from mistletoe.ast_renderer import get_ast
from mistletoe import Document
from mistletoe import block_token
from mistletoe import span_token


@pytest.mark.parametrize('TokenType,test_str',[
    (block_token.Heading, "### This is a heading."),
    (block_token.Paragraph, 'This is literally just a paragraph.'),
    (block_token.Paragraph, 'This is literally just a paragraph. It does contain *some emphasised text*.'),
    (span_token.Emphasis,"*This is another one.*",),
    (span_token.Strong, "__This is a simple document__",),
    (span_token.Strikethrough, "~~Here is a strikethrough for ya~~",),
    (block_token.List, dedent("""\
    1. Testing
    2. Testing.
    3. __Testing...__
        1. Testing inner
        2. Another one...
    """)),
    (block_token.List, dedent("""\
    * Testing
    * *Testing.*
    * Testing...
        - Testing inner
        - Another one...
    """)),
    (block_token.List, dedent("""\
    1. Testing
    2. Testing.
    3. Testing...
        - Testing `inner`
        - Another one...
    """)),
    (block_token.Quote, "> This is a `simple` quote."),
    (span_token.InlineCode, "`this-is-some-hacker-codez: True`",),
    (block_token.CodeFence, dedent("""\
    ```
    def example():
        pass
    ```
    """)),
    (block_token.BlockCode, indent(dedent("""\
    def example():
        pass
    """), '    ')),
    (span_token.Link, "[This is a simple link to the Uoregon site](https://uoregon.edu)"),
    (span_token.Link, "Here is a paragraph [that contains a simple link to the Uoregon site](https://uoregon.edu)..."),
    (span_token.AutoLink, "<https://uoregon.edu>"),
    (block_token.Table, dedent("""\
            | Day     | Meal    | Price |
            | --------|---------|-------|
            | Monday  | pasta   | $6    |
            | Tuesday | chicken | $8    |
    """)),
    (block_token.ThematicBreak, dedent('''
    This is a paragraph before a thematic break.
    
    ---
    
    This is a paragraph after the thematic break.
    ''')),
    (span_token.Image, 'This is how you might share an image ![Silly Alt Text](test.png "Test Title")'),
    (span_token.EscapeSequence, 'These are some common things you might escape: \\, \\`, \\*, \\#'),
    (span_token.EscapeSequence, 'These are some common things you might escape: \\`, \\*, \\#'),
    (span_token.EscapeSequence, 'These are some common things you might escape: \\*, \\#'),
    (span_token.EscapeSequence, 'These are some common things you might escape: \\#'),
    (span_token.LineBreak, 'Testing Testing\n123.'),
    (span_token.RawText, 'Done.'),
])
def test_test(TokenType, test_str):
    # ARRANGE
    token = Document(test_str)
    # Walk the document until we encounter the Token we are interested in.
    token = get_first_token(token, TokenType)

    # ACT
    copied_token = token.copy()

    # ASSERT
    assert isinstance(copied_token, TokenType)
    print(get_ast(copied_token))
    assert get_ast(copied_token) == get_ast(token)


class FoundTokenException(BaseException):
    def __init__(self, token):
        self.token = token


def get_first_token(token, TokenType):
    try:
        _get_first_token(token, TokenType)
    except FoundTokenException as e:
        return e.token
    raise TypeError(f'Could not find token of type {TokenType} in token. Rendered AST printed here:' + str(get_ast(token)))


def _get_first_token(token, TokenType):
    if isinstance(token, TokenType):
        raise FoundTokenException(token)
    elif hasattr(token, 'children'):
        for child_token in token.children:
            _get_first_token(child_token, TokenType)
