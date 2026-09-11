"""Build a .docx fixture carrying known orthographic problems, for manual testing."""

from docx import Document

OUT_PATH = "test.docx"

# Paragraph one. Non-canonical underdots (U+0329, U+0331) with the tone mark
# sitting before the underdot, split across a bold run and an italic run so
# that run-level rewriting can be checked against formatting loss.
BOLD_WORD = "e\u0300\u0329ko\u0301\u0331"
ITALIC_WORD = "\u1ecd\u0300w\u1ecd\u0300"

# Paragraph two. A zero-width space inside a word and curly quotation marks.
INVISIBLES_AND_PUNCTUATION = "\u1ecdm\u1ecd\u200b n\u00e1\u00e0 \u2018d\u00e1ra\u2019"

# Paragraph three. Already canonical, so standardize() should leave it alone.
CLEAN = "\u00c0w\u1ecdn \u1ecdm\u1ecd n\u00e1\u00e0 w\u00e0 n\u00edl\u00e9"


def main():
    document = Document()

    mixed = document.add_paragraph()
    bold_run = mixed.add_run(BOLD_WORD)
    bold_run.bold = True
    mixed.add_run(" ")
    italic_run = mixed.add_run(ITALIC_WORD)
    italic_run.italic = True

    document.add_paragraph(INVISIBLES_AND_PUNCTUATION)
    document.add_paragraph(CLEAN)

    document.save(OUT_PATH)
    print("wrote " + OUT_PATH)


if __name__ == "__main__":
    main()
