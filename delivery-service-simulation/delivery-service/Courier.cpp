#include "Courier.h"


Courier::Courier(int id, City *startingLocation, const Map *map,
                 int distanceLimit)
                 : id(id), day(0), location(startingLocation), map(map),
                 distanceLimit(distanceLimit), remainingDistance(0) {
}


void Courier::deliver(Package *package, City *source, City *destination) {
    // method for commanding courier to deliver a package from source to destination
    // alters the courier's path so that he will eventually go through the needed cities

    // add package to packages to be picked up in the source city
    if (packagesToPickUp.find(source) == packagesToPickUp.end()){
        packagesToPickUp.insert({source, {package}});
    } else {
        packagesToPickUp.at(source).push_back(package);
    }

    // add package to packages to be delivered to the destination city
    if (packagesToDeliver.find(destination) == packagesToDeliver.end()){
        packagesToDeliver.insert({destination, {package}});
    } else {
        packagesToDeliver.at(destination).push_back(package);
    }

    // figure out, how to alter the path
    // if source and destination are in correct order in path, it doesn't need to be altered
    // if only source is in the path, we append path from last city in the current path to destination
    // if neither, we append path from last city in the current path to source and from source to destination
    bool sourceCityInPath = false;
    for (auto &city : path){
        // search for the source city
        // if there is source City in the path, only after that is it relevant to search for destination City
        if (sourceCityInPath == false && city == source){
            sourceCityInPath = true;
        }
        if (sourceCityInPath && city == destination){
            // found source and destination in correct order - does not need to change path
            return;
        }
    }

    if (sourceCityInPath){
        // the package will be picked up along the path, but needs to append path to destination
        appendPathToCity(destination);
        return;
    }

    // source is not in the current path, need to append path to source and then path to destination
    appendPathToCity(source);
    appendPathToCity(destination);
}


void Courier::appendPathToCity(City *destination) {
    // appends shortest path to destination to the current path

    City *fromCity;     // city where the appended path will begin
    if (path.empty()){
        fromCity = location;
    } else {
        fromCity = path.back();
    }

    std::vector<City*> pathToDestination = map->findShortestPath(fromCity, destination);

    // the first city is omitted, because that city is either already in the path or the current location of the courier
    path.insert(path.end(), pathToDestination.begin() + 1, pathToDestination.end());
}


std::vector<std::tuple<int, int, PackageStatus>> Courier::shiftTime(int days) {
    // simulate time - shift is the number of days to be simulated
    // return changes that happened to packages during simulation

    // vector to store changes that happened during simulation
    // stores which package changed status on which day - (packageID, day, newStatus)
    std::vector<std::tuple<int, int, PackageStatus>> changedPackages;

    for (int i = 0; i < days; i++){
        shiftDay(changedPackages);
    }
    return changedPackages;
}

void Courier::shiftDay(std::vector<std::tuple<int, int, PackageStatus>> &changedPackages){
    // simulate one day, alter the passed changedPackages vector

    // if path is empty, just increment the day counter
    if (path.empty()){
        day++;
        return;
    }

    // if the courier ended up halfway the day before, add the distance to the distance limit
    remainingDistance += distanceLimit;

    handleOnLocationDeliveries(changedPackages);        // pick up and deliver packages on current location

    // while the courier can move, move to next city in the path and pick up and deliver packages there
    while (move()){
        handleOnLocationDeliveries(changedPackages);
    }

    day++;
}


void Courier::handleOnLocationDeliveries(std::vector<std::tuple<int, int, PackageStatus>> &changedPackages) {
    // picks up and delivers packages in current location, stores changes in changedPackages

    // pick up all packages on the current location and store them in packagesInDelivery
    if (packagesToPickUp.find(location) != packagesToPickUp.end()){     // if there are any packages on the location
        for (auto &package : packagesToPickUp.at(location)){
            package->changePackageStatus(IN_DELIVERY);          // change their status to IN_DELIVERY
            packagesInDelivery.push_back(package);                        // store the pointers in appropriate field

            changedPackages.emplace_back(package->id, day, package->packageStatus);     // mark the change
        }
        packagesToPickUp.erase(location);       // remove the entry - packages has been picked up
    }

    // deliver all the packages in the current city if they have been picked up
    if (packagesToDeliver.find(location) != packagesToDeliver.end()){  // if there are any packages on the location to be delivered
        for (auto &package : packagesToDeliver.at(location)){

            // if the package is not currently in delivery (was not picked up), skip the iteration
            if (std::find(packagesInDelivery.begin(), packagesInDelivery.end(), package) == packagesInDelivery.end()){
                continue;
            }

            package->changePackageStatus(DELIVERED);        // change the package status
            packagesInDelivery.erase(
                    std::remove(packagesInDelivery.begin(), packagesInDelivery.end(), package),
                    packagesInDelivery.end()
                    );          // remove the package from inDelivery packages

            changedPackages.emplace_back(package->id, day, package->packageStatus);     // mark the change
        }

        // if there are no packages to be delivered on the location, erase the entry
        if (packagesToDeliver.at(location).empty()){
            packagesToDeliver.erase(location);
        }
    }
}


bool Courier::move() {
    // simulate movement, returns bool if the courier has moved to next city in path

    // if the path is empty, courier does not move
    if (path.empty()){
        return false;
    }


    int distance = location->distanceToNeighbouringCity(path[0]);   // distance to next city in path

    // if the distance is bigger than remainingDistance, courier does not move
    if (distance > remainingDistance){
        return false;
    }

    remainingDistance -= distance;      // subtract distance from remaining distance
    location = path[0];                 // change the location to the next city in path
    path.erase(path.begin());   // remove the current city from the path

    // change the location of all packages that are in delivery
    for (auto &package : packagesInDelivery){
        package->changeLocation(location);
    }
    return true;
}