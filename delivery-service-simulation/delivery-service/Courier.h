#pragma once

#include "City.h"
#include "Package.h"
#include "Map.h"
#include <vector>
#include <unordered_map>
#include <tuple>

class Courier{
    int id;
    int day;
    const int distanceLimit;    // how many kms can the courier travel in a day

    int remainingDistance;      // for simulating being halfway between the cities
                                // if the courier can't travel to the next city, because it would surpass the distanceLimit
                                // we store the unused kms here to be used in the next day

    City *location;
    const Map *map;
    std::vector<City*> path;    // the cities where the courier will move to

    std::vector<Package*> packagesInDelivery;                                       // which packages are currently being delivered
    std::unordered_map<City*, std::vector<Package*>, CityHasher> packagesToPickUp;  // which packages need to be picked up at the city
    std::unordered_map<City*, std::vector<Package*>, CityHasher> packagesToDeliver; // which packages need to be delivered to the city
    
    void appendPathToCity(City *destination);

    void shiftDay(std::vector<std::tuple<int, int, PackageStatus>> &changedPackages);
    void handleOnLocationDeliveries(std::vector<std::tuple<int, int, PackageStatus>> &changedPackages);
    bool move();
public:
    Courier(int id, City *startingLocation, const Map *map,
            int distanceLimit);

    void deliver(Package *package, City *source, City *destination);
    std::vector<std::tuple<int, int, PackageStatus>> shiftTime(int days);

    int getId() const {return id;};
    int getDay() const {return day;};
    City* getLocation() const {return location;};
    const Map *getMap() const {return map;};
    std::vector<City*> getPath() const {return path;};

};
