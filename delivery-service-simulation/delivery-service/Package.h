#pragma once

#include <unordered_map>
#include "City.h"

enum PackageStatus {NOT_PICKED_UP, IN_DELIVERY, DELIVERED};
const std::string packageStatusMessages[] {"not picked up", "in delivery", "delivered"};

class Package {
public:
    const int id;
    City *location;
    PackageStatus packageStatus;

    Package(int id, City *location, PackageStatus packageStatus=NOT_PICKED_UP);
    void changeLocation(City *newLocation);
    void changePackageStatus(PackageStatus newStatus);
};
