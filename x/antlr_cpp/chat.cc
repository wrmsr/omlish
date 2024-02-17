#include "ChatVisitor.h"

using namespace std;
using namespace antlr4;

int main(int argc, const char* argv[]) {
    std::ifstream stream;
    stream.open("test.chat");
    
    ANTLRInputStream input(stream);
    ChatLexer lexer(&input);
    CommonTokenStream tokens(&lexer);
    ChatParser parser(&tokens);
    ChatParser::FileContext* tree = parser.file();
    ChatVisitor visitor;
    Chat chat = std::any_cast<Chat>(visitor.visitFile(tree));
    // scene.draw();
    return 0;
}
