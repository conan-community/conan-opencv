#include "opencv2/opencv.hpp"
#include "opencv2/core/utils/logger.hpp"
#include <iostream>
#include <fstream>

bool file_exists(const char *filepath) {
	std::ifstream file(filepath);
	return file.good();
}

int main( int argc, const char** argv ){
    cv::utils::logging::setLogLevel(cv::utils::logging::LOG_LEVEL_DEBUG);
    cv::Mat image = cv::imread(argv[1]);
    if(!file_exists(argv[1])) {
	    std::cerr << "File " << argv[1] << " does not exist!\n";
	    return 1;
    }
    if(image.data == nullptr) {
	std::cerr << "Error: could not load image " << argv[1] << "\n";
	return 1;
    } else {
	std::cout << "Successfully load image " << argv[1] << " of size " << image.size() << "\n";
	return 0;
    }
}
