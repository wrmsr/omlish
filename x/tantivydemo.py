"""
https://tantivy-py.readthedocs.io/en/latest/tutorials/
"""
import pathlib
import tempfile

import tantivy as tv


def _main() -> None:
    # Declaring our schema.
    schema_builder = tv.SchemaBuilder()
    schema_builder.add_text_field("title", stored=True)
    schema_builder.add_text_field("body", stored=True)
    schema_builder.add_integer_field("doc_id", stored=True)
    schema = schema_builder.build()

    # Creating our index (in memory)
    index = tv.Index(schema)

    #

    tmpdir = tempfile.TemporaryDirectory()
    index_path = pathlib.Path(tmpdir.name) / "index"
    index_path.mkdir()
    persistent_index = tv.Index(schema, path=str(index_path))

    #

    schema_builder_tok = tv.SchemaBuilder()
    schema_builder_tok.add_text_field("body", stored=True, tokenizer_name='en_stem')

    #

    writer = index.writer()
    writer.add_document(tv.Document(
        doc_id=1,
        title=["The Old Man and the Sea"],
        body=[
            "He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now "
            "without taking a fish."
        ],
    ))
    # ... and committing
    writer.commit()
    writer.wait_merging_threads()

    #

    # Reload the index to ensure it points to the last commit.
    index.reload()
    searcher = index.searcher()

    #

    query = index.parse_query("fish days", ["title", "body"])
    (best_score, best_doc_address) = searcher.search(query, 3).hits[0]
    best_doc = searcher.doc(best_doc_address)
    assert best_doc["title"] == ["The Old Man and the Sea"]

    #

    complex_query = tv.Query.boolean_query(
        [
            (
                tv.Occur.Must,
                tv.Query.disjunction_max_query(
                    [
                        tv.Query.boost_query(
                            # by default, only the query parser will analyze
                            # your query string
                            index.parse_query("fish", ["title"]),
                            2.0
                        ),
                        tv.Query.boost_query(
                            index.parse_query("eighty-four days", ["body"]),
                            1.5
                        ),
                    ],
                    0.3,
                ),
            )
        ]
    )

    #

    hit_text = best_doc["body"][0]
    print(f"{hit_text=}")
    assert hit_text == (
        "He was an old man who fished alone in a skiff in the "
        "Gulf Stream and he had gone eighty-four days now "
        "without taking a fish."
    )

    snippet_generator = tv.SnippetGenerator.create(
        searcher, query, schema, "body"
    )
    snippet = snippet_generator.snippet_from_doc(best_doc)

    #

    highlights = snippet.highlighted()
    first_highlight = highlights[0]
    assert first_highlight.start == 93
    assert first_highlight.end == 97
    assert hit_text[first_highlight.start:first_highlight.end] == "days"

    #

    html_snippet = snippet.to_html()
    assert html_snippet == (
        "He was an old man who fished alone in a skiff in the "
        "Gulf Stream and he had gone eighty-four <b>days</b> now "
        "without taking a <b>fish</b>"
    )


if __name__ == '__main__':
    _main()
