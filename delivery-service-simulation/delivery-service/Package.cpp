#include "Package.h"

Package::Package(int id, City *location, PackageStatus packageStatus)
                : id(id), location(location), packageStatus(packageStatus){
}

void Package::changeLocation(City *newLocation) {
    location = newLocation;
};

void Package::changePackageStatus(PackageStatus newStatus) {
    packageStatus = newStatus;
}