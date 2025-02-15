// Copyright 2005, Google Inc.
// All rights reserved.

#include <iostream>
#include "gtest/gtest.h"

#include "Map.h"

using namespace ::testing;

TEST(TestMap, simpleFileLoading){
    Map map("small_map.txt");

    auto a = (map.getCity("A"));
    auto b = (map.getCity("B"));
    auto c = (map.getCity("C"));
    ASSERT_TRUE(a->isNeighbourTo(b));
    ASSERT_TRUE(a->isNeighbourTo(c));
    ASSERT_FALSE(b->isNeighbourTo(b));

    ASSERT_EQ(a->distanceToNeighbouringCity(b), 10);
    ASSERT_EQ(a->distanceToNeighbouringCity(c), 20);
    ASSERT_EQ(b->distanceToNeighbouringCity(c), -1);
}


TEST(TestMap, badMapFile) {
    ASSERT_THROW({
                     try {
                         Map map("non_existing_map_file.txt");
                     }
                     catch( const MapFileException &e) {
                         ASSERT_STREQ(
                                 "Failed action with \"non_existing_map_file.txt\" map file: map file not found",
                                 e.what());
                         throw;
                     }
                     }, MapFileException);
    ASSERT_THROW({
                     try {
                         Map map("bad_map_file.txt");
                     }
                     catch( const MapFileException &e) {
                         ASSERT_STREQ(
                                 "Failed action with \"bad_map_file.txt\" map file: following line not structured as "
                                 "- [cityName1, cityName2, distance]:\n"
                                 "\"A C K\"",
                                 e.what());
                         throw;
                     }
                 }, MapFileException);
}


TEST(TestMap, testProperPathCreation){
    Map map("dijkstra_test_map.txt");

    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto d = map.getCity("D");
    auto e = map.getCity("E");
    auto f = map.getCity("F");
    auto g = map.getCity("G");

    ASSERT_EQ(a->distanceToNeighbouringCity(a), -1);
    ASSERT_EQ(a->distanceToNeighbouringCity(b), 4);
    ASSERT_EQ(b->distanceToNeighbouringCity(c), 2);
    ASSERT_EQ(c->distanceToNeighbouringCity(g), -1);    // shouldn't be neighbours
    ASSERT_EQ(e->distanceToNeighbouringCity(f), 3);     // should not be rewritten by E F 2
    ASSERT_EQ(e->distanceToNeighbouringCity(d), -1);    // D E -3 shouldn't add them as neighbours
}


TEST(TestMap, testDijkstra){
    Map map("dijkstra_test_map.txt");
    auto a = map.getCity("A");
    auto b = map.getCity("B");
    auto c = map.getCity("C");
    auto d = map.getCity("D");
    auto e = map.getCity("E");
    auto f = map.getCity("F");
    auto g = map.getCity("G");

    // proper paths
    std::vector<City*> foundPath = map.findShortestPath(a, f);
    std::vector<City*> expectedPath = {a, c, e, f};
    ASSERT_EQ(foundPath, expectedPath);

    foundPath = map.findShortestPath(b, f);
    expectedPath = {b, c, e, f};
    ASSERT_EQ(foundPath, expectedPath);

    foundPath = map.findShortestPath(f, b);
    expectedPath = {f, e, c, b};
    ASSERT_EQ(foundPath, expectedPath);

    foundPath = map.findShortestPath(d, d);
    expectedPath = {d};
    ASSERT_EQ(foundPath, expectedPath);

    foundPath = map.findShortestPath(a, c);
    expectedPath = {a, c};
    ASSERT_EQ(foundPath, expectedPath);

    foundPath = map.findShortestPath(c, f);
    expectedPath = {c, e, f};
    ASSERT_EQ(foundPath, expectedPath);

    // distances
    foundPath = map.findShortestPath(c, g);
    ASSERT_EQ(map.findDistanceOfPath(foundPath), 5);

    foundPath = map.findShortestPath(e, e);
    ASSERT_EQ(map.findDistanceOfPath(foundPath), 0);

    foundPath = {d};
    ASSERT_EQ(map.findDistanceOfPath(foundPath), 0);

    foundPath = {a, b, g};
    ASSERT_EQ(map.findDistanceOfPath(foundPath), -1);

    foundPath = {};
    ASSERT_EQ(map.findDistanceOfPath(foundPath), 0);
}