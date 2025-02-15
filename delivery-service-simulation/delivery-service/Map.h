# pragma once

# include <vector>
# include <format>
#include <iostream>
#include <fstream>
#include <unordered_map>
#include <sstream>
#include <algorithm>
#include "City.h"

constexpr auto mapFileExceptionMessage {"Failed action with \"{}\" map file: {}"};

class Map {
    std::unordered_map<std::string, City> cities;

    void createPath(std::string &firstCityName, std::string &secondCityName, int &distance);

    // methods for Dijkstra's algorithm:
    City* dijkstraStep(
            City *currentCity,
            std::unordered_map<City*, std::pair<int, std::string>, CityHasher> &distances,
            std::vector<City*> &visited
        ) const;
    std::vector<City*> makePathFromDijkstraResult(
            City *beginCity, City *endCity,
            std::unordered_map<City*, std::pair<int, std::string>, CityHasher> &distances
        ) const;

public:
    Map(const std::string &mapFile);
    std::vector<City*> findShortestPath(City *beginCity, City *endCity) const;
    int findDistanceOfPath(std::vector<City*> path) const;
    City* getCity(const std::string &name) const;
};


class MapFileException : public std::exception {
    std::string msg;
public:
    MapFileException(const std::string &mapFile, const std::string &failure)
        : msg(std::format(mapFileExceptionMessage, mapFile, failure)) {
    }

    const char *what() const noexcept override {return msg.c_str();}
};