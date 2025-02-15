// Copyright 2005, Google Inc.
// All rights reserved.

#include <iostream>
#include "gtest/gtest.h"

#include "City.h"

using namespace ::testing;

TEST(TestCity, addingNeighbours){
    City a("A");
    City b("B");
    City c("C");

    auto ptr_a = &a;
    auto ptr_b = &b;
    auto ptr_c = &c;

    a.addNeighbour(ptr_b, 10);
    a.addNeighbour(ptr_c, 20);
    ASSERT_EQ(a.getName(), "A");
    ASSERT_TRUE(a.isNeighbourTo(ptr_b));
    ASSERT_TRUE(a.isNeighbourTo(ptr_c));
    ASSERT_FALSE(a.isNeighbourTo(ptr_a));
    ASSERT_FALSE(b.isNeighbourTo(ptr_a));
}


TEST(TestCity, distanceToNeighbours){
    City a("A");
    City b("B");
    City c("C");

    auto ptr_a = &a;
    auto ptr_b = &b;
    auto ptr_c = &c;

    a.addNeighbour(ptr_b, 10);
    ASSERT_EQ(a.distanceToNeighbouringCity(ptr_a), -1);
    ASSERT_EQ(a.distanceToNeighbouringCity(ptr_b), 10);
    ASSERT_EQ(a.distanceToNeighbouringCity(ptr_c), -1);

    a.addNeighbour(ptr_c, 20);
    ASSERT_EQ(a.distanceToNeighbouringCity(ptr_c), 20);
}


TEST(TestCity, addingInvalidNeighbour){
    City a("A");
    City a2("A");
    City b("B");
    auto ptr_a = &a;
    auto ptr_a2 = &a2;
    auto ptr_b = &b;

    a.addNeighbour(ptr_a, 0);
    ASSERT_FALSE(a.isNeighbourTo(ptr_a));
    a.addNeighbour(ptr_a2, 2);
    ASSERT_FALSE(a.isNeighbourTo(ptr_a2));

    a.addNeighbour(ptr_b, -5);
    ASSERT_FALSE(a.isNeighbourTo(ptr_b));

    a.addNeighbour(ptr_b, 1);
    ASSERT_TRUE(a.isNeighbourTo(ptr_b));
    a.addNeighbour(ptr_b, 5);
    ASSERT_EQ(a.distanceToNeighbouringCity(ptr_b), 1);
}


TEST(TestCity, testEqualityOperators){
    City a("A");
    City a2("A");
    City b("B");

    ASSERT_TRUE(a == a);
    ASSERT_TRUE(a == a2);
    ASSERT_FALSE(a == b);

    ASSERT_FALSE(a != a);
    ASSERT_FALSE(a != a2);
    ASSERT_TRUE(a != b);
}