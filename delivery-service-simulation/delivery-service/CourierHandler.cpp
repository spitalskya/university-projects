#include "CourierHandler.h"


CourierHandler::CourierHandler(int numberOfBasicCouriers, int numberOfFirstClassCouriers,
                               const std::string &startingLocation, Map &map,
                               int distanceLimitBasicCourier,
                               int distanceLimitFirstClassCourier) : map(map) {
    // creates passed number of basic and first class couriers

    // get the starting city for all couriers
    City *startingCity = map.getCity(startingLocation);
    if (startingCity == nullptr){
        throw CourierHandlerConstructionException("courier starting city invalid");
    }

    if (numberOfBasicCouriers < 1 || numberOfFirstClassCouriers < 1){
        throw CourierHandlerConstructionException("all courier counts need to be at least 1");
    }

    // create basic couriers with unique IDS
    for (int i = 0; i < numberOfBasicCouriers; i++) {
        int id = generateBasicCourierId();
        basicCouriers.insert({
            id,
            Courier(id, startingCity, &map, distanceLimitBasicCourier)
        });
    }

    // create first class couriers with unique IDS
    for (int i = 0; i < numberOfFirstClassCouriers; i++) {
        int id = generateFirstClassCourierId();
        firstClassCouriers.insert({
            id,
            Courier(id, startingCity, &map, distanceLimitFirstClassCourier)
        });
    }
}


Courier* CourierHandler::getCourier(int courierId) const {
    // return pointer to instance of Courier with given index
    // if there is no courier with such an index, throw exception

    if (basicCouriers.find(courierId) != basicCouriers.end()){
        return const_cast<Courier *>(&basicCouriers.at(courierId));
    }
    if (firstClassCouriers.find(courierId) != firstClassCouriers.end()){
        return const_cast<Courier *>(&firstClassCouriers.at(courierId));
    }
    throw CourierNotFoundException(std::to_string(courierId));
}


int CourierHandler::assignPackage(Package *package, City *source, City *destination,
                                   CourierType courierType) {
    // handle which courier should deliver the package
    // return price for distance that courier needs to travel to deliver the package multiplied by courier price
    // we can be sure that this package was not assigned in the past since method DeliveryService::sendPackage always creates a new one

    // get only couriers of relevant type
    std::unordered_map<int, Courier> &relevantCouriers = courierType == BASIC ? basicCouriers : firstClassCouriers;     // sorry

    // trying to find somebody that can travel the least distance from his current position to destination through source
    // if source and destination are in the path, calculate distance to destination through current path
    // if source is in the path, calculate distance from path + path to destination
    // else, calculate distance from path + path to source + path to destination
    Courier *bestCourier = &relevantCouriers.begin()->second;       // so far the best courier for delivery
    int bestDistance = std::numeric_limits<int>::max();             // so far the shortest distance needed to be travelled
                                                                    // by the best courier to deliver the package

    for (auto &courier : relevantCouriers){
        bool sourceInPath = false;                  // whether the source city is in path of the current courier
        bool destinationInPath = false;             // whether the destination city is in path of the current courier
        std::vector<City*> pathIfCourierWouldDeliver;   // how would the courier's path look like if he had to deliver the package
        std::vector<City*> currentPathOfCourier = courier.second.getPath();     // current path of the courier

        for (auto &city : currentPathOfCourier){
            pathIfCourierWouldDeliver.push_back(city);      // add city to updated path

            // if city is the source city, mark it
            if (city == source){
                sourceInPath = true;
            }

            // if city is the destination city and the source city was also found, mark it
            if (sourceInPath && city == destination){
                destinationInPath = true;
                break;
            }
        }

        // if source city is not in the path, extend the courier's path by path from
        // either his last city in the path or current location to source city
        if (sourceInPath == false){
            City *lastCity;
            if (currentPathOfCourier.empty()){
                lastCity = courier.second.getLocation();
            } else {
                lastCity = currentPathOfCourier.back();
            }
            std::vector<City*> extendPath = map.findShortestPath(lastCity, source);
            pathIfCourierWouldDeliver.insert(
                    pathIfCourierWouldDeliver.end(), extendPath.begin() + 1, extendPath.end()
            );
        }

        // if destination city is not in the current path, extend the path in similar manner
        if (destinationInPath == false){
            City *lastCity;
            if (pathIfCourierWouldDeliver.empty()){
                lastCity = courier.second.getLocation();
            } else {
                lastCity = pathIfCourierWouldDeliver.back();

            }
            std::vector<City*> extendPath = map.findShortestPath(lastCity, destination);
            pathIfCourierWouldDeliver.insert(
                    pathIfCourierWouldDeliver.end(), extendPath.begin() + 1, extendPath.end()
            );
        }


        // calculate the distance of the path relevant for the package
        // need to add starting point of the path
        pathIfCourierWouldDeliver.insert(pathIfCourierWouldDeliver.begin(), bestCourier->getLocation());
        int distanceIfCourierWouldDeliver = map.findDistanceOfPath(pathIfCourierWouldDeliver);

        // determine whether the distance is better than the best distance before, if yes, change the best courier
        if (distanceIfCourierWouldDeliver < bestDistance){
            bestCourier = &courier.second;
            bestDistance = distanceIfCourierWouldDeliver;
        }
    }

    bestCourier->deliver(package, source, destination);     // assign the courier with delivery

    // calculate the price for distance for customer
    int priceForDistance;
    if (courierType == BASIC){
        priceForDistance = bestDistance * basicCourierStats.at("pricePerDistance");
    } else {
        priceForDistance = bestDistance * firstClassCourierStats.at("pricePerDistance");
    }

    return priceForDistance;
}


std::vector<std::tuple<int, int, PackageStatus>> CourierHandler::shiftTime(int days) {
    // simulate time shift for basic and first class couriers

    std::vector<std::tuple<int, int, PackageStatus>> changedPackages;

    for (auto &courier : basicCouriers){
        std::vector<std::tuple<int, int, PackageStatus>> courierChangedPackages = courier.second.shiftTime(days);
        changedPackages.insert(changedPackages.end(), courierChangedPackages.begin(), courierChangedPackages.end());
    }
    for (auto &courier : firstClassCouriers){
        std::vector<std::tuple<int, int, PackageStatus>> courierChangedPackages = courier.second.shiftTime(days);
        changedPackages.insert(changedPackages.end(), courierChangedPackages.begin(), courierChangedPackages.end());
    }

    return changedPackages;
}
