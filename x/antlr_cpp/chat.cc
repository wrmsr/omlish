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
    virtual std::any visitChildren(tree::ParseTree *node) override {
        // std::cout << node->toString() << std::endl;
        std::cout << node->toStringTree() << std::endl;
        return ChatVisitor::visitChildren(node);
    }

    virtual std::any visitChat(ChatParser::ChatContext *context) override { return visitChildren(context); }

    virtual std::any visitLine(ChatParser::LineContext *context) override { return visitChildren(context); };

    virtual std::any visitName(ChatParser::NameContext *context) override { return visitChildren(context); };

    virtual std::any visitCommand(ChatParser::CommandContext *context) override { return visitChildren(context); };

    virtual std::any visitMessage(ChatParser::MessageContext *context) override { return visitChildren(context); };

    virtual std::any visitEmoticon(ChatParser::EmoticonContext *context) override { return visitChildren(context); };

    virtual std::any visitLink(ChatParser::LinkContext *context) override { return visitChildren(context); };

    virtual std::any visitColor(ChatParser::ColorContext *context) override { return visitChildren(context); };

    virtual std::any visitMention(ChatParser::MentionContext *context) override { return visitChildren(context); };
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
