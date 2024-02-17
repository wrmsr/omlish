/*
https://tomassetti.me/getting-started-antlr-cpp/
https://github.com/gabriele-tomassetti/antlr-cpp/blob/master/ImageVisitor.cpp
*/
#include <iostream>

#include "antlr4-runtime.h"

#include "ChatLexer.h"
#include "ChatVisitor.h"

using namespace std;
using namespace antlr4;

class ChatVisitorImpl : public ChatVisitor {
public:
    std::any visitChat(ChatParser::ChatContext *context) { return visitChildren(context); }

    std::any visitLine(ChatParser::LineContext *context) { return visitChildren(context); };

    std::any visitName(ChatParser::NameContext *context) { return visitChildren(context); };

    std::any visitCommand(ChatParser::CommandContext *context) { return visitChildren(context); };

    std::any visitMessage(ChatParser::MessageContext *context) { return visitChildren(context); };

    std::any visitEmoticon(ChatParser::EmoticonContext *context) { return visitChildren(context); };

    std::any visitLink(ChatParser::LinkContext *context) { return visitChildren(context); };

    std::any visitColor(ChatParser::ColorContext *context) { return visitChildren(context); };

    std::any visitMention(ChatParser::MentionContext *context) { return visitChildren(context); };
};

int main(int argc, const char* argv[]) {
    std::ifstream stream;
    stream.open("test.chat");
    
    ANTLRInputStream input(stream);
    ChatLexer lexer(&input);
    CommonTokenStream tokens(&lexer);
    ChatParser parser(&tokens);
    ChatParser::ChatContext* tree = parser.chat();
    ChatVisitorImpl visitor;
    visitor.visitChat(tree);
    // Chat chat = std::any_cast<Chat>(visitor.visitFile(tree));
    // scene.draw();
    return 0;
}
