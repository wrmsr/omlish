from ..json import render_obj_json_ui_text


def test_render():
    t = render_obj_json_ui_text({
        'hi': ['there', '!'],
    })

    print(t)
