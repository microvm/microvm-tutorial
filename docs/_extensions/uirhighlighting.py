def setup(app):
    import uirlexer
    app.add_lexer("uir", uirlexer.UirLexer())
    #app.add_lexer("uir", True)
