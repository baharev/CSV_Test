#include <cstdlib>
#include <fstream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc != 3)
        return 1;
    std::string name(argv[2]);
    std::ifstream src(name + ".rgf", std::ios::binary);
    if (!src.good())
        return 1;
    std::ofstream dst(name + ".csv", std::ios::binary);
    dst << src.rdbuf();
    std::system(("mkdir -p "+name).c_str());
    std::ofstream dummy(name + "/log.txt", std::ios::binary);
}

