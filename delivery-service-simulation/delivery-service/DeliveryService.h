#pragma once

#include "Map.h"
#include "Package.h"
#include "CourierHandler.h"
#include <map>
#include <unordered_map>
#include <format>
#include <memory>
#include <sstream>
#include <fstream>
#include <tuple>

constexpr auto loggingFileExceptionMessage {"Logging file error: {}"};
constexpr auto postReceiptFormatExceptionMessage {
    "Post receipt \"{}\" had wrong format: {}"
};
constexpr auto loggingMessage{"Status of package {} was changed on the day {} to: {}\n"};

const std::map<int, int, std::greater<>> weightMultipliers{
        {10000, 7},
        {5000, 5},
        {2000, 4},
        {1000, 3},
        {100, 2}
};


class DeliveryService {
    const std::string loggingFile;

    int day;
    std::unordered_map<int, Package> packages;
    CourierHandler courierHandler;
    Map &map;

    int packageNextId = 1;
    int packageIdOffset = 100;

    int generatePackageId() {return packageIdOffset + packageNextId++;};
    int deliveryPriceCalculation(int weight, int priceForDistance) const;
    void log(std::vector<std::tuple<int, int, PackageStatus>> &changedPackages) const;
public:
    DeliveryService(const std::string &loggingFile, Map &map,
                    int numberOfBasicCouriers, int numberOfFirstClassCouriers,
                    const std::string &startingLocation,
                    int distanceLimitBasicCourier = basicCourierStats.at("distanceLimit"),
                    int distanceLimitFirstClassCourier = firstClassCourierStats.at("distanceLimit"));

    std::unordered_map<std::string, int> sendPackage(const std::string &postReceipt);
    std::string getPackageInformation(int packageId) const;
    bool shiftTime(int days);
};


class LoggingFileException : public std::exception {
    std::string msg;
public:
    LoggingFileException(const std::string &exceptionType)
        : msg(std::format(loggingFileExceptionMessage, exceptionType)) {
    }

    const char *what() const noexcept override {return msg.c_str();}
};


class PostReceiptFormatException : public std::exception {
    std::string msg;
public:
    PostReceiptFormatException(const std::string &postReceipt, const std::string &failure)
            : msg(std::format(postReceiptFormatExceptionMessage, postReceipt, failure)) {
    }

    const char *what() const noexcept override {return msg.c_str();}
};