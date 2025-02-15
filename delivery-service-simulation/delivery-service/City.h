#pragma once

#include <unordered_map>
#include <string>
#include "City.fwd.h"
#include "CityHasher.h"

struct CityEqual {
    bool operator()(const City *lhs, const City *rhs) const;
};

class City {
    std::unordered_map<City*, int, CityHasher, CityEqual> neighbours;
    std::string name;

public:
    City(const std::string &name);

    void addNeighbour(City *city, int distance);
    bool isNeighbourTo(City *city) const;
    int distanceToNeighbouringCity(City *city) const;

    std::string getName() const { return name; };
    std::unordered_map<City*, int, CityHasher, CityEqual> getNeighbours() const {return neighbours;};

    bool operator ==(const City &other) const;
    bool operator !=(const City &other) const;
};

