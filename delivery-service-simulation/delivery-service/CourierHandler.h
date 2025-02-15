#pragma once

#include <string>
#include <unordered_map>
#include <format>
#include <tuple>
#include "Courier.h"
#include "City.h"
#include "Map.h"


const std::unordered_map<std::string, int> basicCourierStats {{"distanceLimit", 150},         // in kms
                                                              {"pricePerDistance", 5}};       // in euro-cents/km
const std::unordered_map<std::string, int> firstClassCourierStats {{"distanceLimit", 400},
                                                                   {"pricePerDistance", 10}};

constexpr auto courierNotFoundExceptionMessage {"Courier with ID {} was not found"};
constexpr auto courierHandlerConstructionExceptionMessage {
    "Following problem occurred during CourierHandler construction: {}"
};

enum CourierType {BASIC, FIRST_CLASS};


class CourierHandler {
    std::unordered_map<int, Courier> basicCouriers;
    std::unordered_map<int, Courier> firstClassCouriers;
    Map &map;

    int basicCourierNextId = 1;
    int basicCourierIdOffset = 1000;
    int firstClassCourierNextId = 1;
    int firstClassCourierIdOffset = 2000;

    int generateBasicCourierId() {return basicCourierIdOffset + basicCourierNextId++;};
    int generateFirstClassCourierId() {return firstClassCourierIdOffset + firstClassCourierNextId++;};
public:
    CourierHandler(int numberOfBasicCouriers, int numberOfFirstClassCouriers,
                   const std::string &startingLocation, Map &map,
                   int distanceLimitBasicCourier,
                   int distanceLimitFirstClassCourier);

    int assignPackage(Package *package, City *source, City *destination, CourierType courierType);
    std::vector<std::tuple<int, int, PackageStatus>> shiftTime(int days);

    Courier* getCourier(int courierId) const;
    std::unordered_map<int, Courier> getBasicCouriers() {return basicCouriers;};
    std::unordered_map<int, Courier> getFirstClassCouriers() {return firstClassCouriers;};

};


class CourierHandlerConstructionException : public std::exception {
    std::string msg;
public:
    CourierHandlerConstructionException(const std::string &problem)
            : msg(std::format(courierHandlerConstructionExceptionMessage, problem)) {
    }

    const char *what() const noexcept override {return msg.c_str();}
};


class CourierNotFoundException : public std::exception {
    std::string msg;
public:
    CourierNotFoundException(const std::string &courierIndex)
        : msg(std::format(courierNotFoundExceptionMessage, courierIndex)) {
    }

    const char *what() const noexcept override {return msg.c_str();}
};
