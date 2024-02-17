#include "parser/ChatVisitor.h"

using namespace std;
using namespace antlr4;

int main(int argc, const char* argv[]) {
    std::ifstream stream;
    stream.open("test.chat");
    
    ANTLRInputStream input(stream);
    SceneLexer lexer(&input);
    CommonTokenStream tokens(&lexer);
    SceneParser parser(&tokens);    
    SceneParser::FileContext* tree = parser.file();
    ImageVisitor visitor;
    Scene scene = std::any_cast<Scene>(visitor.visitFile(tree));
    scene.draw();
    return 0;
}
