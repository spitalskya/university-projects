#include <iostream>
#include "City.h"


bool CityEqual::operator()(const City *lhs, const City *rhs) const {
    // equality comparator for City pointers for hash-map of neighbours
    return lhs->getName() == rhs->getName();
}

City::City(const std::string &name) : name(name){
}

void City::addNeighbour(City *city, int distance) {
    // if passed city is already not a neighbour, add it as a neighbour with passed distance
    if (distance < 0 || name == city->name || neighbours.find(city) != neighbours.end()){
        return;
    }

    neighbours.insert({city, distance});
}

bool City::isNeighbourTo(City *city) const {
    // determine whether this city is neighbouring to passed city
    return neighbours.find( city) != neighbours.end();
}

int City::distanceToNeighbouringCity(City *city) const {
    // return distance to passed city, -1 if the city is not a neighbour
    if(isNeighbourTo(city)){
        return neighbours.at(city);
    }

    return -1;
}

bool City::operator==(const City &other) const{
    return name == other.name;
}

bool City::operator!=(const City &other) const{
    return name != other.name;
}
