#pragma once

#include "../../../../../problem/AProblem.h"
#include "../../../../../method/methods/SO/GPHH/CGPHH.h"

class CGPHHFactory
{
public:
    static CGPHH *CreateGPHH(SConfigMap *configMap, AProblem &problem, AInitialization *initialization,
                         ACrossover *crossover,
                         AMutation *mutation);
    static void DeleteObjects();
private:
    static std::vector<float> *objectiveWeights;
    static CFitnessTournament *fitnessTournament;
};
