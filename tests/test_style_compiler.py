from comicstrip_tutor.styles.compiler import compile_style_guide


def test_compile_style_guide_returns_template_theme_metadata() -> None:
    compiled = compile_style_guide(
        template_id="misconception-first",
        theme_id="sci-fi-lab",
        audience_level="beginner",
    )
    assert compiled.template.template_id == "misconception-first"
    assert compiled.theme.theme_id == "sci-fi-lab"
    assert "Theme" in compiled.style_text
    assert "Template" in compiled.style_text
