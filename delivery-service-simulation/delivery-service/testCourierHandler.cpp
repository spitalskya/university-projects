// Copyright 2005, Google Inc.
// All rights reserved.

#include <iostream>
#include "gtest/gtest.h"

#include "CourierHandler.h"
#include "Map.h"

using namespace ::testing;


TEST(TestCourierHandler, properConstructorTest){
    Map map("small_map.txt");
    CourierHandler courierHandler(5, 5, "A", map,
                                  basicCourierStats.at("distanceLimit"),
                                  firstClassCourierStats.at("distanceLimit"));

    ASSERT_EQ(courierHandler.getCourier(1001)->getId(), 1001);
    ASSERT_EQ(courierHandler.getCourier(2005)->getId(), 2005);
    ASSERT_THROW({
                     try {
                         courierHandler.getCourier(2006)->getId();
                     }
                     catch( const CourierNotFoundException &e) {
                         ASSERT_STREQ("Courier with ID 2006 was not found", e.what());
                         throw;
                     }
                 }, CourierNotFoundException);

    ASSERT_EQ(courierHandler.getCourier(1001)->getMap(), &map);
    ASSERT_EQ(courierHandler.getCourier(1002)->getMap()->getCity("A"), map.getCity("A"));
    ASSERT_EQ(courierHandler.getCourier(2002)->getMap()->getCity("B"), map.getCity("B"));
}


TEST(TestCourierHandler, packageAssignment){
    // set-up
    Map map("dijkstra_test_map.txt");
    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto d = map.getCity("D");
    auto e = map.getCity("E");
    auto f = map.getCity("F");
    auto g = map.getCity("G");

    Package package1(101, a, NOT_PICKED_UP);
    Package package2(102, f, NOT_PICKED_UP);
    Package package3(103, c, NOT_PICKED_UP);
    Package package4(104, c, NOT_PICKED_UP);

    std::vector<City*> expectedPathBasic, expectedPathFirstClass1, expectedPathFirstClass2;
    std::vector<City*> emptyPath = {};

    // end of set-up

    CourierHandler courierHandler(2, 2, "A", map,
                                  4, 6);

    Courier *basic1 = courierHandler.getCourier(1001);
    Courier *basic2 = courierHandler.getCourier(1002);
    Courier *firstClass1 = courierHandler.getCourier(2001);
    Courier *firstClass2 = courierHandler.getCourier(2002);


    int priceForDistance = courierHandler.assignPackage(&package1, package1.location, f, BASIC);
    expectedPathBasic = {c, e, f};
    // the package should have been assigned to one of the couriers
    ASSERT_EQ(priceForDistance, 40);
    ASSERT_TRUE(
            ((basic1->getPath() == expectedPathBasic && basic2->getPath() == emptyPath)
            || (basic1->getPath() == emptyPath && basic2->getPath() == expectedPathBasic))
        );
    ASSERT_EQ(firstClass1->getPath(), emptyPath);
    ASSERT_EQ(firstClass2->getPath(), emptyPath);


    priceForDistance = courierHandler.assignPackage(&package2, package2.location, g, FIRST_CLASS);
    expectedPathFirstClass1 = {c, e, f, d, g};
    // package should be assigned to one of the first class couriers
    ASSERT_EQ(priceForDistance, 120);
    ASSERT_TRUE(
            ((basic1->getPath() == expectedPathBasic && basic2->getPath() == emptyPath)
             || (basic1->getPath() == emptyPath && basic2->getPath() == expectedPathBasic))
    );
    ASSERT_TRUE(
            ((firstClass1->getPath() == expectedPathFirstClass1 && firstClass2->getPath() == emptyPath)
             || (firstClass1->getPath() == emptyPath && firstClass2->getPath() == expectedPathFirstClass1))
    );


    priceForDistance = courierHandler.assignPackage(&package3, package3.location, e, BASIC);
    // package should be assigned to the basic courier already assigned with package,
    // because the source and the destination are already in his path
    // so path of the courier should not change and the price of the package should be for the path a-c-e
    ASSERT_EQ(priceForDistance, 25);
    ASSERT_TRUE(
            ((basic1->getPath() == expectedPathBasic && basic2->getPath() == emptyPath)
             || (basic1->getPath() == emptyPath && basic2->getPath() == expectedPathBasic))
    );
    ASSERT_TRUE(
            ((firstClass1->getPath() == expectedPathFirstClass1 && firstClass2->getPath() == emptyPath)
             || (firstClass1->getPath() == emptyPath && firstClass2->getPath() == expectedPathFirstClass1))
    );


    priceForDistance = courierHandler.assignPackage(&package4, package4.location, b, FIRST_CLASS);
    expectedPathFirstClass2 = {c, b};
    // package should be assigned to the first class courier without any assigned package,
    // because the destination is not in its path, and it is more advantageous to send the second courier for it
    // with path a-c-b instead of appending e-c-b to already a long path of the another courier
    ASSERT_EQ(priceForDistance, 60);
    ASSERT_TRUE(
            ((basic1->getPath() == expectedPathBasic && basic2->getPath() == emptyPath)
             || (basic1->getPath() == emptyPath && basic2->getPath() == expectedPathBasic))
    );
    ASSERT_TRUE(
            ((firstClass1->getPath() == expectedPathFirstClass1 && firstClass2->getPath() == expectedPathFirstClass2)
             || (firstClass1->getPath() == expectedPathFirstClass2 && firstClass2->getPath() == expectedPathFirstClass1))
    );
}


TEST(TestCourierHandler, timeShift){
    // set-up
    Map map("dijkstra_test_map.txt");
    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto e = map.getCity("E");
    auto f = map.getCity("F");
    auto g = map.getCity("G");

    Package package1(101, a, NOT_PICKED_UP);
    Package package2(102, f, NOT_PICKED_UP);
    Package package3(103, c, NOT_PICKED_UP);
    Package package4(104, c, NOT_PICKED_UP);

    CourierHandler courierHandler(2, 2, "A", map,
                                  4, 6);

    std::vector<std::tuple<int, int, PackageStatus>> expectedChangedPackages;
    // end of set-up

    // same package assignment logic as before
    courierHandler.assignPackage(&package1, package1.location, f, BASIC);
    courierHandler.assignPackage(&package2, package2.location, g, FIRST_CLASS);
    courierHandler.assignPackage(&package3, package3.location, e, BASIC);
    courierHandler.assignPackage(&package4, package4.location, b, FIRST_CLASS);

    // so the paths should be:
    // from a to {c, e, f} for one of the basic couriers
    // from a to {} for another one of the basic couriers
    // from a to {c, e, f, d, g} for one of the first class couriers
    // from a to {c, b} for another one of the first class couriers

    auto changedPackages = courierHandler.shiftTime(1);
    // package1 should be picked up from city a by basic courier
    // package3 should be picked up from city c by the same basic courier
    // package2 shouldn't be picked up, one of the first class couriers should be in city e
    // package4 should be picked up from city c and delivered to city b by another first class courier
    expectedChangedPackages = {
            {101, 0, IN_DELIVERY},
            {103, 0, IN_DELIVERY},
            {104, 0, IN_DELIVERY},
            {104, 0, DELIVERED}
    };

    // need to sort the changed packages so that we can compare vectors
    // biggest priority has the day, then status and then ID
    auto changedPackagesComparator = [](const auto &tuple1, const auto &tuple2) {
        return std::get<1>(tuple1) < std::get<1>(tuple2)
                || (std::get<1>(tuple1) == std::get<1>(tuple2) && std::get<2>(tuple1) < std::get<2>(tuple2))
                || (std::get<1>(tuple1) == std::get<1>(tuple2) && std::get<2>(tuple1) == std::get<2>(tuple2) && std::get<0>(tuple1) < std::get<0>(tuple2));
    };

    std::sort(changedPackages.begin(), changedPackages.end(), changedPackagesComparator);
    ASSERT_EQ(changedPackages, expectedChangedPackages);
    ASSERT_EQ(package1.location, c);
    ASSERT_EQ(package2.location, f);
    ASSERT_EQ(package3.location, c);
    ASSERT_EQ(package4.location, b);


    changedPackages = courierHandler.shiftTime(3);
    // package1 should be delivered to city f on the day 1
    // package2 should picked up in the city f on the day 1
    // package2 should be delivered to city g on the day 1
    // package3 should be delivered to city e on the day 1
    // package4 was already delivered
    expectedChangedPackages = {
            {102, 1, IN_DELIVERY},
            {101, 1, DELIVERED},
            {102, 1, DELIVERED},
            {103, 1, DELIVERED}
    };
    std::sort(changedPackages.begin(), changedPackages.end(), changedPackagesComparator);
    ASSERT_EQ(changedPackages, expectedChangedPackages);
    ASSERT_EQ(package1.location, f);
    ASSERT_EQ(package2.location, g);
    ASSERT_EQ(package3.location, e);
    ASSERT_EQ(package4.location, b);
}
