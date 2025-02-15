// Copyright 2005, Google Inc.
// All rights reserved.

#include "gtest/gtest.h"
#include "Package.h"
#include "City.h"

using namespace ::testing;

TEST(TestPackage, constructorAndSettersTests){
    City a("A");
    auto ptr_a = &a;

    Package package(101, ptr_a, NOT_PICKED_UP);
    ASSERT_EQ(package.id, 101);
    ASSERT_EQ(package.location, ptr_a);
    ASSERT_EQ(package.packageStatus, NOT_PICKED_UP);

    City b("B");
    auto ptr_b = &b;

    package.changeLocation(ptr_b);
    package.changePackageStatus(IN_DELIVERY);
    ASSERT_EQ(package.id, 101);
    ASSERT_EQ(package.location, ptr_b);
    ASSERT_EQ(package.packageStatus, IN_DELIVERY);
}
