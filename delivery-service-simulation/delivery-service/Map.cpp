#include "Map.h"

Map::Map(const std::string &mapFile) {
    // constructs Map instance from given mapFile
    // the lines of mapFile should have this format [cityName1, cityName2, distance]
    //
    // for each line, the constructor creates City instances with given names if they are not already created
    // then it adds the cities as neighbours to each other with given distance

    std::ifstream inFile(mapFile);
    if(!inFile){
        throw MapFileException(mapFile, "map file not found");
    }

    // load city structure from file
    std::string line;
    while(std::getline(inFile, line)) {
        std::stringstream ss(line);
        std::string firstCityName;
        std::string secondCityName;
        int distance;

        if (ss >> firstCityName >> secondCityName >> distance) {
            // create the two cities if necessary and connect them
            createPath(firstCityName, secondCityName, distance);
        } else {
            throw MapFileException(
                    mapFile,
                    std::format(
                            "following line not structured as - [cityName1, cityName2, distance]:\n\"{}\"",
                            line
                            )
                );
        }
    }
}

void Map::createPath(std::string &firstCityName, std::string &secondCityName, int &distance) {
    // creates path between two cities with given distance, creates the cities if they have not yet been created

    // create cities if they do not exist
    if(cities.find(firstCityName) == cities.end()){
        cities.insert({firstCityName, City(firstCityName)});
    }
    if(cities.find(secondCityName) == cities.end()){
        cities.insert(std::make_pair(secondCityName, City(secondCityName)));
    }

    // make the two cities neighbours
    auto firstCity = &cities.at(firstCityName);
    auto secondCity = &cities.at(secondCityName);

    firstCity->addNeighbour(secondCity, distance);
    secondCity->addNeighbour(firstCity, distance);
}


City* Map::getCity(const std::string &name) const{
    // if city with passed name exists, returns pointer to it, else returns nullptr
    if (cities.find(name) == cities.end()){
        return nullptr;
    }
    return const_cast<City *>(&cities.at(name));
}

int Map::findDistanceOfPath(std::vector<City*> path) const{
    // goes through vector of cities and sums up the distances between adjacent elements
    // if two adjacent elements (cities) are not neighbours, returns -1

    if (path.empty()){
        return 0;
    }

    int distance = 0;

    for (size_t i = 0; i < path.size() - 1; i++){
        int incrementDistance = path[i]->distanceToNeighbouringCity(path[i + 1]);
        if (incrementDistance == -1){
            return -1;
        }
        distance += incrementDistance;
    }
    return distance;
}

std::vector<City*> Map::findShortestPath(City *beginCity, City *endCity) const{
    // utilizes Dijkstra's algorithm to find the shortest path between two cities
    // expects the map to have only one component

    // table of cities as keys
    // first value entry is the current shortest distance to the city (-1 instead of infinity)
    // second value entry is the previous city name in the shortest path yet
    std::unordered_map<City*, std::pair<int, std::string>, CityHasher> distances;
    distances.reserve(cities.size());

    for (auto &cityEntry : cities){
        int distance = -1;
        if (&cityEntry.second == beginCity){
            // distance to begincity is 0
            distance = 0;
        }
        distances.insert(
                {
                const_cast<City*>(&cityEntry.second),       // city as key
                    std::make_pair(distance, "")      // infinite distance and no city in the shortest path yet
                }
            );
    }

    City *currentCity = beginCity;
    std::vector<City*> visited = {currentCity};      // vector of visited cities

    while (visited.size() < cities.size()){         // while there is an unvisited city
        currentCity = dijkstraStep(currentCity, distances, visited);    // perform one step of an Dijkstra's algorithm
    }

    // from final table of Dijkstra's algorithm, create the shortest path between beginCity and endCity
    return makePathFromDijkstraResult(beginCity, endCity, distances);
}


City* Map::dijkstraStep(City *currentCity, std::unordered_map<City*, std::pair<int, std::string>, CityHasher> &distances,
                       std::vector<City *> &visited) const{
    // performs one step of Dijkstra's algorithm

    int currentDistance = distances.at(currentCity).first;      // shortest distance from beginCity to currentCity

    // update paths from current city
    for(auto &neighbour : currentCity->getNeighbours()){
        // neighbours is a pair of City* and distance to that city
        int distanceBefore = distances.at(neighbour.first).first;
        int distanceAfter = currentDistance + neighbour.second;

        // if distance to neighbouring city is shorter through current city, update it in the table
        if (distanceBefore == -1 || distanceBefore > distanceAfter){
            distances.at(neighbour.first) = std::make_pair(distanceAfter, currentCity->getName());
        }
    }

    // move to the closest unvisited neighbour of currentCity
    City *whereToMove;   // stub city (any unvisited city)
    for (auto &city : currentCity->getNeighbours()){
        if(std::find(visited.begin(), visited.end(), city.first) == visited.end()){
            whereToMove = const_cast<City *>(city.first);
        }
    }
    int moveDistance = distances[whereToMove].first;    // distance to city where we want to go next

    for (auto &neighbour : currentCity->getNeighbours()){
        // check if the city has been visited
        auto inVisited = std::find(visited.begin(), visited.end(),neighbour.first);

        if (distances[neighbour.first].first < moveDistance && inVisited == visited.end()){
            // if the distance to current neighbour is less then the city already stored in whereToMove,
            // and it has not been visited - update the city (and the distance) to where the algorithm should move

            whereToMove = const_cast<City *>(&cities.at(neighbour.first->getName()));
            moveDistance = distances[whereToMove].first;
        }
    }

    visited.push_back(whereToMove);     // add city where the algorithm will move to visited
    return whereToMove;                 // return the city from where the algorithm should perform the next step
}

std::vector<City*> Map::makePathFromDijkstraResult(
        City *beginCity, City *endCity,
        std::unordered_map<City*, std::pair<int, std::string>, CityHasher> &distances) const {

    // from table of Dijkstra's algorithm result, construct the corresponding path
    // (there is always one, because we expect only one component on the map graph
    // the table distances looks like
    // [city] : ([the shortest distance to city from beginCity] [name of the city before in the shortest path])

    std::vector<City*> path;    // the shortest path between beginCity and endCity will be stored here

    std::string currentCityName = endCity->getName();       // construction is going backwards
    while (currentCityName != beginCity->getName()){        // go backwards through table entries until you find beginCity
        path.push_back(const_cast<City *>(&cities.at(currentCityName)));
        currentCityName = distances.at(const_cast<City *>(&cities.at(currentCityName))).second;
    }
    path.push_back(const_cast<City *>(&cities.at(currentCityName)));    // add beginCity to the path

    std::reverse(path.begin(), path.end());
    return path;
}