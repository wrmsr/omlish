from ..building import D
from ..building import d
from ..rendering import Renderer


def test_dom():
    root = d('html').add(
        d('head').add(
            d('title', 'hi'),
        ),
        d('body').add(
            d('svg', id='chart', width='600', height='300'),
            d('div', id='tooltip', class_='tooltip', x_data='{}'),
        ),
    )

    print(root)
    print(Renderer.render_to_str(root))
    print(Renderer.render_to_str(root, indent=2))
    print()

    #

    root = D.html(
        D.head(
            D.title('hi'),
        ),
        D.body(
            D.svg(id='chart', width='600', height='300'),
            D.div(id='tooltip', class_='tooltip', x_data='{}'),
        ),
    )

    print(root)
    print(Renderer.render_to_str(root))
    print(Renderer.render_to_str(root, indent=2))
    print()

    #

    root = D.html(
        D.head(
            D.script(src="..."),
            D.script(
                "alert('Hello World')"
            ),
        ),
        D.body(
            D.div(
                D.h1(id="title").add("This is a title"),
                D.p("This is a big paragraph of text"),
            ),
        ),
    )

    print(root)
    print(Renderer.render_to_str(root))
    print(Renderer.render_to_str(root, indent=2))
    print()
