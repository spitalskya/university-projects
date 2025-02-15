#include "DeliveryService.h"


DeliveryService::DeliveryService(const std::string &loggingFile, Map &map,
                                 int numberOfBasicCouriers, int numberOfFirstClassCouriers,
                                 const std::string &startingLocation,
                                 int distanceLimitBasicCourier,
                                 int distanceLimitFirstClassCourier)
                                 : loggingFile(loggingFile), day(0),
                                   map(map),
                                   courierHandler(numberOfBasicCouriers, numberOfFirstClassCouriers,
                                                  startingLocation, map,
                                                  distanceLimitBasicCourier, distanceLimitFirstClassCourier) {
    // initialize all fields and create the logging file

    std::ofstream outputFile(loggingFile);
    if (outputFile.is_open() == false) {
        throw LoggingFileException("failed to create");
    }
}


std::string DeliveryService::getPackageInformation(int packageId) const {
    // for a package with given ID, return a formatted string of it's ID, current location and status

    if (packages.find(packageId) == packages.end()){
        return std::format("Package with ID {} was not found", packageId);
    }

    std::ostringstream oss;
    const Package &package = packages.at(packageId);

    oss << "Package ID: " << package.id << "\n";
    oss << "Current location: " << package.location->getName() << "\n";
    oss << "Current status: " << packageStatusMessages[package.packageStatus];
    return oss.str();
}


bool DeliveryService::shiftTime(int days) {
    // simulate time days for all couriers, log changes of statuses of packages
    // return false if days is negative

    if (days < 0){
        return false;
    }

    auto changedPackages = courierHandler.shiftTime(days);
    log(changedPackages);
    day += days;
    return true;
}

std::unordered_map<std::string, int> DeliveryService::sendPackage(const std::string &postReceipt){
    // method for creating a package and ordering the courierHandler to deliver it
    // the post receipt needs to be formatted like - "sourceCityName,destinationCityName,weightInGrams,typeOfCourierWanted"
    // returns hash-map of generated ID of the package and price for it's delivery

    // get the data from postReceipt string
    std::istringstream iss(postReceipt);
    std::string sourceLocation, destinationLocation, weightString, type;
    if ((std::getline(iss, sourceLocation, ',')
        && std::getline(iss, destinationLocation, ',')
        && std::getline(iss, weightString, ',')
        && std::getline(iss, type, ',')) == false){
        throw PostReceiptFormatException(
                postReceipt, "not in format \"sourceCityName,destinationCityName,weightInGrams,typeOfCourierWanted\""
                );
    }

    City *sourceCity = map.getCity(sourceLocation);             // get source city from its name
    City *destinationCity = map.getCity(destinationLocation);   // get destination city from its name

    // if either city does not exist, throw an exception
    if (sourceCity == nullptr || destinationCity == nullptr){
        throw PostReceiptFormatException(postReceipt, "at least one of the city names was not valid");
    }

    // try to convert weight string to weight int
    int weight;
    try {
        weight = std::stoi(weightString);
    } catch (const std::invalid_argument &e) {
        throw PostReceiptFormatException(postReceipt, "weight was not an integer");
    }

    // try to convert courier type string into CourierType
    CourierType courierType;
    if (type == "basic"){
        courierType = BASIC;
    } else if (type == "firstClass"){
        courierType = FIRST_CLASS;
    } else {
        throw PostReceiptFormatException(postReceipt, "courier type was invalid");
    }

    // all checks passed

    // create package
    int id = generatePackageId();
    packages.insert({
        id,
        Package(id, sourceCity, NOT_PICKED_UP)
    });

    // assign the package to a courier and calculate its price (price for distance * weight multiplicator)
    packages.at(id);
    int priceForDistance = courierHandler.assignPackage(const_cast<Package*>(&packages.at(id)), sourceCity, destinationCity, courierType);
    int price = deliveryPriceCalculation(weight, priceForDistance);

    // log the created package
    std::vector<std::tuple<int, int, PackageStatus>> newPackage{{id, day, NOT_PICKED_UP}};
    log(newPackage);

    return {
            {"ID", id},
            {"price", price}
    };
}


void DeliveryService::log(std::vector<std::tuple<int, int, PackageStatus>> &changedPackages) const{
    // method for logging changes
    // elements of vector of changed packages need to be in format - (packageID, dayOfChange, newPackageStatus)

    // sort the changes
    // biggest priority has the day, then status and then ID
    auto changedPackagesComparator = [](const auto &tuple1, const auto &tuple2) {
        return std::get<1>(tuple1) < std::get<1>(tuple2)
               || (std::get<1>(tuple1) == std::get<1>(tuple2) && std::get<2>(tuple1) < std::get<2>(tuple2))
               || (std::get<1>(tuple1) == std::get<1>(tuple2) && std::get<2>(tuple1) == std::get<2>(tuple2) && std::get<0>(tuple1) < std::get<0>(tuple2));
    };
    std::sort(changedPackages.begin(), changedPackages.end(), changedPackagesComparator);


    // write each change into the logging file
    for (auto &changedPackage : changedPackages){
        int id = std::get<0>(changedPackage);
        int dayOfChange = std::get<1>(changedPackage);
        PackageStatus packageStatus = std::get<2>(changedPackage);

        std::ofstream logFile(loggingFile, std::ios::app);
        if (logFile.is_open() == false){
            throw LoggingFileException("failed to append");
        }
        logFile << std::format(loggingMessage,
                               id, dayOfChange, packageStatusMessages[packageStatus]);
    }
}


int DeliveryService::deliveryPriceCalculation(int weight, int priceForDistance) const {
    // return final price - price for distance multiplied by weight multiplicator

    for (auto &weightMultiplier : weightMultipliers){
        if (weightMultiplier.first <= weight){
            return weightMultiplier.second * priceForDistance;
        }
    }
    return priceForDistance;
}
