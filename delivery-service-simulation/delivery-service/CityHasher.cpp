#include "CityHasher.h"
#include "City.h"
#include <string>

std::size_t CityHasher::operator()(const City *ptr) const {
    return std::hash<std::string>{}(ptr->getName());
}
