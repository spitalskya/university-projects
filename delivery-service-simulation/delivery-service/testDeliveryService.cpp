// Copyright 2005, Google Inc.
// All rights reserved.

#include <iostream>
#include "gtest/gtest.h"
#include <iterator>

#include "DeliveryService.h"

using namespace ::testing;


template <typename K, typename V>
bool operator==(const std::unordered_map<K, V> &map1, const std::unordered_map<K, V> &map2) {
    if (map1.size() != map2.size()) {
        return false;
    }

    for (auto &pair1 : map1) {
        auto pair2 = map2.find(pair1.first);
        if (pair2 == map2.end() || pair2->second != pair1.second) {
            std::cout << pair1.first << " " << pair1.second << std::endl;
            std::cout << pair2->first << " " << pair2->second << std::endl;
            return false;
        }
    }

    return true;
}


TEST(TestDeliveryService, constructorTest){
    Map map("dijkstra_test_map.txt");
    std::string loggingFileName = "logging_file.txt";

    DeliveryService ds(loggingFileName, map, 5, 1, "A");

    std::ifstream loggingFile(loggingFileName);
    ASSERT_TRUE(loggingFile.is_open());

    std::string contents;
    loggingFile >> contents;
    ASSERT_EQ(contents, "");
}


TEST(TestDeliveryService, sendingPackages){
    Map map("dijkstra_test_map.txt");
    std::string loggingFileName = "logging_file.txt";
    DeliveryService ds(loggingFileName, map, 2, 2, "A");

    std::unordered_map<std::string, int> expectedInfoFromPackageSending;

    auto infoFromPackageSending = ds.sendPackage("A,F,10,basic");
    expectedInfoFromPackageSending = {
            {"ID", 101},
            {"price", 40*1}
    };
    ASSERT_TRUE(infoFromPackageSending == expectedInfoFromPackageSending);

    infoFromPackageSending = ds.sendPackage("F,G,150,firstClass");
    expectedInfoFromPackageSending = {
            {"ID", 102},
            {"price", 120*2}
    };
    ASSERT_TRUE(infoFromPackageSending == expectedInfoFromPackageSending);

    infoFromPackageSending = ds.sendPackage("C,E,100000,basic");
    expectedInfoFromPackageSending = {
            {"ID", 103},
            {"price", 25*7}
    };
    ASSERT_TRUE(infoFromPackageSending == expectedInfoFromPackageSending);


    infoFromPackageSending = ds.sendPackage("C,B,1,firstClass");
    expectedInfoFromPackageSending = {
            {"ID", 104},
            {"price", 60*1}
    };
    ASSERT_TRUE(infoFromPackageSending == expectedInfoFromPackageSending);

    std::ifstream loggingFile(loggingFileName);
    std::string contents((std::istreambuf_iterator<char>(loggingFile)), std::istreambuf_iterator<char>());
    ASSERT_EQ(
            contents,
            "Status of package 101 was changed on the day 0 to: not picked up\n"
            "Status of package 102 was changed on the day 0 to: not picked up\n"
            "Status of package 103 was changed on the day 0 to: not picked up\n"
            "Status of package 104 was changed on the day 0 to: not picked up\n"
        );
}

TEST(TestDeliveryService, sendingInvalidPackages) {
    Map map("dijkstra_test_map.txt");
    std::string loggingFileName = "logging_file.txt";
    DeliveryService ds(loggingFileName, map, 2, 2, "A");

    ASSERT_THROW({
                     try {
                         ds.sendPackage("C,B,1");
                     }
                     catch( const PostReceiptFormatException &e) {
                         ASSERT_STREQ(
                                 "Post receipt \"C,B,1\" had wrong format: "
                                 "not in format \"sourceCityName,destinationCityName,weightInGrams,typeOfCourierWanted\"",
                                 e.what()
                             );
                         throw;
                     }
                 }, PostReceiptFormatException);

    ASSERT_NO_THROW(ds.sendPackage("C,B,1,basic,unnecessary,info,here"));     // everything after first entry is thrown away

    ASSERT_THROW({
                     try {
                         ds.sendPackage("C,T,1,firstClass");
                     }
                     catch( const PostReceiptFormatException &e) {
                         ASSERT_STREQ(
                                 "Post receipt \"C,T,1,firstClass\" had wrong format: "
                                 "at least one of the city names was not valid",
                                 e.what()
                         );
                         throw;
                     }
                 }, PostReceiptFormatException);

    ASSERT_NO_THROW(ds.sendPackage("C,B,1.5,firstClass"));    // decimal grams are omitted

    ASSERT_THROW({
                     try {
                         ds.sendPackage("C,B,K,firstClass");
                     }
                     catch( const PostReceiptFormatException &e) {
                         ASSERT_STREQ(
                                 "Post receipt \"C,B,K,firstClass\" had wrong format: "
                                 "weight was not an integer",
                                 e.what()
                         );
                         throw;
                     }
                 }, PostReceiptFormatException);

    ASSERT_THROW({
                     try {
                         ds.sendPackage("C,B,7,express");
                     }
                     catch( const PostReceiptFormatException &e) {
                         ASSERT_STREQ(
                                 "Post receipt \"C,B,7,express\" had wrong format: "
                                 "courier type was invalid",
                                 e.what()
                         );
                         throw;
                     }
                 }, PostReceiptFormatException);

    std::ifstream loggingFile(loggingFileName);
    std::string contents((std::istreambuf_iterator<char>(loggingFile)), std::istreambuf_iterator<char>());
    ASSERT_EQ(
            contents,
            "Status of package 101 was changed on the day 0 to: not picked up\n"
            "Status of package 102 was changed on the day 0 to: not picked up\n"
        );
}


TEST(TestDeliveryService, timeShift){
    // logic of proper assignment and movement explained and tested in TestCourierHandler-timeShift
    Map map("dijkstra_test_map.txt");
    std::string loggingFileName = "logging_file.txt";
    DeliveryService ds(loggingFileName, map, 2, 2, "A",
                       4, 6);

    ds.sendPackage("A,F,10,basic");
    ds.sendPackage("F,G,150,firstClass");
    ds.sendPackage("C,E,100000,basic");
    ds.sendPackage("C,B,1,firstClass");


    ds.shiftTime(1);
    std::ifstream loggingFile(loggingFileName);
    std::string contents((std::istreambuf_iterator<char>(loggingFile)), std::istreambuf_iterator<char>());
    ASSERT_EQ(
            contents,
            "Status of package 101 was changed on the day 0 to: not picked up\n"
            "Status of package 102 was changed on the day 0 to: not picked up\n"
            "Status of package 103 was changed on the day 0 to: not picked up\n"
            "Status of package 104 was changed on the day 0 to: not picked up\n"
            "Status of package 101 was changed on the day 0 to: in delivery\n"
            "Status of package 103 was changed on the day 0 to: in delivery\n"
            "Status of package 104 was changed on the day 0 to: in delivery\n"
            "Status of package 104 was changed on the day 0 to: delivered\n"
    );
    loggingFile.close();

    ds.shiftTime(1);
    std::ifstream loggingFile2(loggingFileName);
    std::string contents2((std::istreambuf_iterator<char>(loggingFile2)), std::istreambuf_iterator<char>());
    ASSERT_EQ(
            contents2,
            "Status of package 101 was changed on the day 0 to: not picked up\n"
            "Status of package 102 was changed on the day 0 to: not picked up\n"
            "Status of package 103 was changed on the day 0 to: not picked up\n"
            "Status of package 104 was changed on the day 0 to: not picked up\n"
            "Status of package 101 was changed on the day 0 to: in delivery\n"
            "Status of package 103 was changed on the day 0 to: in delivery\n"
            "Status of package 104 was changed on the day 0 to: in delivery\n"
            "Status of package 104 was changed on the day 0 to: delivered\n"
            "Status of package 102 was changed on the day 1 to: in delivery\n"
            "Status of package 101 was changed on the day 1 to: delivered\n"
            "Status of package 102 was changed on the day 1 to: delivered\n"
            "Status of package 103 was changed on the day 1 to: delivered\n"
    );
}


TEST(TestCourierHandler, packageInformation){
    Map map("dijkstra_test_map.txt");
    std::string loggingFileName = "logging_file.txt";
    DeliveryService ds(loggingFileName, map, 2, 2, "A",
                       4, 6);

    ds.sendPackage("A,F,10,basic");
    ds.sendPackage("F,G,150,firstClass");
    ds.sendPackage("C,E,100000,basic");
    ds.sendPackage("C,B,1,firstClass");

    ASSERT_EQ(
            ds.getPackageInformation(101),
            "Package ID: 101\n"
            "Current location: A\n"
            "Current status: not picked up"
    );

    ds.shiftTime(1);
    ASSERT_EQ(
            ds.getPackageInformation(101),
            "Package ID: 101\n"
            "Current location: C\n"
            "Current status: in delivery"
        );
    ASSERT_EQ(
            ds.getPackageInformation(104),
            "Package ID: 104\n"
            "Current location: B\n"
            "Current status: delivered"
    );
    ds.shiftTime(3);
    ASSERT_EQ(
            ds.getPackageInformation(102),
            "Package ID: 102\n"
            "Current location: G\n"
            "Current status: delivered"
    );

    ASSERT_EQ(
            ds.getPackageInformation(105),
            "Package with ID 105 was not found"
    );
}

TEST(TestDeliveryService, stressTest){
    Map map("slovak_map.txt");
    std::string loggingFileName = "logging_file_stress.txt";
    DeliveryService ds(loggingFileName, map, 1, 1,
                       "BanskaBystrica");

    ASSERT_NO_THROW({
        ds.sendPackage("Komarno,Trencin,171,basic");
        ds.sendPackage("NoveZamky,Kosice,471,firstClass");
        ds.sendPackage("Trencin,Lucenec,905,firstClass");
        ds.sendPackage("Komarno,StaraLubovna,614,firstClass");
        ds.sendPackage("NoveZamky,Bardejov,805,firstClass");
        ds.sendPackage("ZiarNadHronom,Martin,417,basic");
        ds.shiftTime(4);
        ds.sendPackage("VranovNadToplou,Bardejov,312,basic");
        ds.sendPackage("DunajskaStreda,Komarno,772,firstClass");
        ds.sendPackage("Bratislava,RimavskaSobota,135,basic");
        ds.sendPackage("Humenne,ZiarNadHronom,767,basic");
        ds.sendPackage("Martin,Bratislava,235,basic");
        ds.sendPackage("Lucenec,Partizanske,169,firstClass");
        ds.sendPackage("Trebisov,Partizanske,369,firstClass");
        ds.sendPackage("Bratislava,Presov,993,firstClass");
        ds.sendPackage("Bardejov,Partizanske,526,basic");
        ds.sendPackage("Kezmarok,Zvolen,608,basic");
        ds.shiftTime(4);
        ds.shiftTime(1);
        ds.sendPackage("Zilina,Svidnik,112,firstClass");
        ds.sendPackage("Topolcany,Lucenec,212,firstClass");
        ds.shiftTime(1);
        ds.sendPackage("Humenne,Trencin,97,basic");
        ds.sendPackage("Lucenec,Topolcany,265,basic");
        ds.sendPackage("Bardejov,Bratislava,519,basic");
        ds.sendPackage("Michalovce,Trencin,316,basic");
        ds.sendPackage("Levice,Komarno,371,basic");
        ds.sendPackage("DunajskaStreda,Trebisov,747,firstClass");
        ds.sendPackage("DunajskaStreda,Bratislava,751,basic");
        ds.sendPackage("Bratislava,Partizanske,343,firstClass");
        ds.sendPackage("Partizanske,Trencin,135,basic");
        ds.sendPackage("Presov,Zilina,670,firstClass");
        ds.sendPackage("DunajskaStreda,Poprad,643,basic");
        ds.sendPackage("Nitra,Michalovce,344,basic");
        ds.sendPackage("Prievidza,Bardejov,573,basic");
        ds.sendPackage("Nitra,Komarno,158,basic");
        ds.shiftTime(1);
        ds.sendPackage("Kosice,RimavskaSobota,174,firstClass");
        ds.sendPackage("Prievidza,Nitra,947,basic");
        ds.sendPackage("Martin,DunajskaStreda,824,firstClass");
        ds.sendPackage("Bardejov,Michalovce,351,firstClass");
        ds.sendPackage("Humenne,BanskaBystrica,225,basic");
        ds.sendPackage("Poprad,Presov,217,firstClass");
        ds.sendPackage("Nitra,Komarno,375,firstClass");
        ds.sendPackage("BanskaBystrica,RimavskaSobota,50,firstClass");
        ds.sendPackage("Trencin,BanskaBystrica,215,firstClass");
        ds.sendPackage("Nitra,Michalovce,322,firstClass");
        ds.sendPackage("Trebisov,Humenne,53,firstClass");
        ds.sendPackage("RimavskaSobota,DunajskaStreda,449,firstClass");
        ds.sendPackage("ZiarNadHronom,Presov,563,basic");
        ds.shiftTime(1);
        ds.sendPackage("Presov,Bratislava,234,basic");
        ds.sendPackage("Prievidza,Zvolen,765,basic");
        ds.sendPackage("StaraLubovna,Kezmarok,638,basic");
        ds.sendPackage("Kezmarok,Martin,475,firstClass");
        ds.sendPackage("RimavskaSobota,Partizanske,134,basic");
        ds.sendPackage("BanskaBystrica,Martin,896,basic");
        ds.sendPackage("Lucenec,Kosice,637,firstClass");
        ds.sendPackage("Levice,Topolcany,361,basic");
        ds.sendPackage("Topolcany,Trebisov,575,firstClass");
        ds.sendPackage("Kosice,Kezmarok,330,firstClass");
        ds.sendPackage("VranovNadToplou,ZiarNadHronom,241,firstClass");
        ds.sendPackage("Zvolen,StaraLubovna,181,firstClass");
        ds.sendPackage("Michalovce,RimavskaSobota,193,basic");
        ds.sendPackage("Zvolen,Zilina,685,basic");
        ds.shiftTime(4);
        ds.sendPackage("Poprad,RimavskaSobota,876,basic");
        ds.sendPackage("Michalovce,BanskaBystrica,63,basic");
        ds.sendPackage("Michalovce,Komarno,198,firstClass");
        ds.sendPackage("NoveZamky,Martin,610,firstClass");
        ds.sendPackage("BanskaBystrica,NoveZamky,237,basic");
        ds.shiftTime(3);
        ds.sendPackage("Poprad,Trencin,531,firstClass");
        ds.sendPackage("Komarno,BanskaBystrica,630,basic");
        ds.sendPackage("Zilina,Kezmarok,147,firstClass");
        ds.sendPackage("Humenne,Trebisov,514,basic");
        ds.sendPackage("RimavskaSobota,Zilina,353,basic");
        ds.sendPackage("DunajskaStreda,Presov,891,basic");
        ds.sendPackage("Bardejov,Zilina,290,basic");
        ds.sendPackage("Poprad,RimavskaSobota,887,firstClass");
        ds.sendPackage("Lucenec,Martin,917,firstClass");
        ds.shiftTime(3);
        ds.shiftTime(3);
        ds.sendPackage("Partizanske,StaraLubovna,694,firstClass");
        ds.shiftTime(3);
        ds.sendPackage("Humenne,NoveZamky,64,basic");
        ds.sendPackage("VranovNadToplou,Kezmarok,997,basic");
        ds.sendPackage("Komarno,Bardejov,903,basic");
        ds.sendPackage("Trencin,Bratislava,498,firstClass");
        ds.shiftTime(1);
        ds.sendPackage("Trencin,Topolcany,53,basic");
        ds.sendPackage("Humenne,DunajskaStreda,409,firstClass");
        ds.shiftTime(4);
        ds.shiftTime(2);
        ds.sendPackage("Humenne,Svidnik,777,firstClass");
        ds.sendPackage("Topolcany,Bratislava,53,firstClass");
        ds.sendPackage("Poprad,Bratislava,547,basic");
        ds.sendPackage("Levice,Svidnik,496,basic");
        ds.sendPackage("Humenne,Bratislava,507,basic");
        ds.sendPackage("Kezmarok,BanskaBystrica,346,firstClass");
        ds.shiftTime(10);
    });
}