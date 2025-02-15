#pragma once

#include <functional>
#include <memory>
#include "City.fwd.h"

struct CityHasher {
    std::size_t operator()(const City *ptr) const;
};
