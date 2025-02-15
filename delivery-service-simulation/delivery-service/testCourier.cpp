// Copyright 2005, Google Inc.
// All rights reserved.

#include <iostream>
#include "gtest/gtest.h"

#include "CourierHandler.h"
#include "Package.h"
#include "Map.h"

using namespace ::testing;

TEST(TestCourier, constructorTest){
    Map map("small_map.txt");
    City *a = map.getCity("A");

    Courier courier(1001, a, &map, basicCourierStats.at("distanceLimit"));
    ASSERT_EQ(courier.getId(), 1001);
    ASSERT_EQ(courier.getLocation(), a);
    ASSERT_EQ(courier.getMap(), &map);
    std::vector<City*> emptyPath = {};
    ASSERT_EQ(courier.getPath(), emptyPath);
}


TEST(TestCourier, pathChangesUponDeliver){
    Map map("dijkstra_test_map.txt");
    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto e = map.getCity("E");
    auto f = map.getCity("F");

    Package package1(101, f, NOT_PICKED_UP);

    Courier courier(1000, a, &map, basicCourierStats.at("distanceLimit"));

    courier.deliver(&package1, package1.location, b);
    std::vector<City*> courierPath = courier.getPath();
    std::vector<City*> expectedPath = {c, e, f, e, c, b};
    ASSERT_EQ(courierPath, expectedPath);

    Package package2(102, b, NOT_PICKED_UP);
    courier.deliver(&package2, package2.location, b);
    courierPath = courier.getPath();
    ASSERT_EQ(courierPath, expectedPath);       // path should not be changed

    Package package3(103, e, NOT_PICKED_UP);
    courier.deliver(&package3, package3.location, a);
    courierPath = courier.getPath();
    expectedPath = {c, e, f, e, c, b, a};
    ASSERT_EQ(courierPath, expectedPath);       // source in the path, destination not, should add path from last city to destination

    Package package4(104, a, NOT_PICKED_UP);
    courier.deliver(&package4, package4.location, f);
    courierPath = courier.getPath();
    expectedPath = {c, e, f, e, c, b, a, c, e, f};
    ASSERT_EQ(courierPath, expectedPath);       // destination is before the source, so should add path from last city to destination
}


TEST(TestCourier, testTimeShiftOnePackage){
    Map map("dijkstra_test_map.txt");
    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto f = map.getCity("F");

    Package package(101, f, NOT_PICKED_UP);

    Courier courier(1, a, &map, 4);

    courier.deliver(&package, package.location, b); // path = {c, e, f, e, c, b};

    std::vector<std::tuple<int, int, PackageStatus>> changedPackages = courier.shiftTime(1);
    std::vector<std::tuple<int, int, PackageStatus>> expectedChangedPackages = {};
    // courier should travel to c but not pick up a package
    ASSERT_EQ(courier.getLocation(), c);
    ASSERT_EQ(package.location, f);
    ASSERT_EQ(package.packageStatus, NOT_PICKED_UP);
    ASSERT_EQ(changedPackages, expectedChangedPackages);

    changedPackages = courier.shiftTime(2);
    expectedChangedPackages = {{101, 1, IN_DELIVERY}};
    // courier should move to c through f where he should have picked up the package on day 1
    ASSERT_EQ(courier.getLocation(), c);
    ASSERT_EQ(package.location, c);
    ASSERT_EQ(package.packageStatus, IN_DELIVERY);
    ASSERT_EQ(changedPackages, expectedChangedPackages);

    changedPackages = courier.shiftTime(5);
    expectedChangedPackages = {{101, 3, DELIVERED}};
    // courier should finish the path at b where he should have dropped off the package on day 3
    ASSERT_EQ(courier.getLocation(), b);
    ASSERT_EQ(courier.getDay(), 8);
    ASSERT_EQ(package.location, b);
    ASSERT_EQ(package.packageStatus, DELIVERED);
    ASSERT_EQ(changedPackages, expectedChangedPackages);
}

TEST(TestCourier, testTimeShiftOverlappingPackages){
    Map map("dijkstra_test_map.txt");
    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto d = map.getCity("D");
    auto e = map.getCity("E");
    auto f = map.getCity("F");
    auto g = map.getCity("G");

    Package package1(101, c, NOT_PICKED_UP);
    Package package2(102, e, NOT_PICKED_UP);
    Courier courier(1, f, &map, 4);

    courier.deliver(&package1, package1.location, b);   // path = {e, c, b}
    courier.deliver(&package2, package2.location, a);   // path = {e, c, b, a}

    std::vector<City*> courierPath = courier.getPath();
    std::vector<City*> expectedPath = {e, c, b, a};
    ASSERT_EQ(courierPath, expectedPath);

    std::vector<std::tuple<int, int, PackageStatus>> changedPackages = courier.shiftTime(1);
    std::vector<std::tuple<int, int, PackageStatus>> expectedChangedPackages = {{102, 0, IN_DELIVERY}, {101, 0, IN_DELIVERY}};
    // in one day, courier should travel through e and c, picking up both packages
    ASSERT_EQ(courier.getLocation(), c);
    ASSERT_EQ(package1.location, c);
    ASSERT_EQ(package2.location, c);
    ASSERT_EQ(changedPackages, expectedChangedPackages);

    changedPackages = courier.shiftTime(1);
    expectedChangedPackages = {{101, 1, DELIVERED}};
    // in another day, courier should travel to b, delivering package 101
    ASSERT_EQ(courier.getLocation(), b);
    ASSERT_EQ(package1.location, b);
    ASSERT_EQ(package2.location, b);
    ASSERT_EQ(changedPackages, expectedChangedPackages);

    changedPackages = courier.shiftTime(5);
    expectedChangedPackages = {{102, 2, DELIVERED}};
    // courier should end up in a, delivering package 102
    ASSERT_EQ(courier.getLocation(), a);
    ASSERT_EQ(package1.location, b);
    ASSERT_EQ(package2.location, a);
    ASSERT_EQ(changedPackages, expectedChangedPackages);
}